# Automated AMI and Snapshot Deletion
#
# @author Valerii Vainkop <vainkop@gmail.com>
#
# This script will search for all AMIs having a tag with "DeleteOn"
# on it. As soon as we have the AMIs list, we loop through each images
# and reference the AMIs. We check that the latest daily backup
# succeeded then we store every image that's reached its DeleteOn tag's date for
# deletion. We loop through the AMIs, deregister them and remove all the
# snapshots associated with that AMI.


import boto3
import collections
import datetime
import time
import os
import sys

ec = boto3.client('ec2', os.environ['region'])
ec2 = boto3.resource('ec2', os.environ['region'])
images = ec2.images.filter(Owners=[os.environ['ami_owner']],
                           Filters=[{'Name': 'tag-key', 'Values': ['DeleteOn']}])

label_id = os.environ['label_id']
instance_id = os.environ['instance_id']

def lambda_handler(event, context):
    to_tag = collections.defaultdict(list)

    date = datetime.datetime.now()
    date_fmt = date.strftime('%Y-%m-%d')

    imagesList = []

    # Set to true once we confirm we have a backup taken today
    backupSuccess = False

    # Loop through each image
    for image in images:

        try:
            if image.tags is not None:
                deletion_date = [
                    t.get('Value') for t in image.tags
                    if t['Key'] == 'DeleteOn'][0]
                delete_date = time.strptime(deletion_date, "%m-%d-%Y")
        except IndexError:
            deletion_date = False
            delete_date = False

        # Our other Lambda Function names its AMIs label_id-
        # We now know these images are auto created
        if image.name.startswith(label_id + '-' + instance_id):

            try:
                if image.tags is not None:
                    deletion_date = [
                        t.get('Value') for t in image.tags
                        if t['Key'] == 'DeleteOn'][0]
                    delete_date = time.strptime(deletion_date, "%m-%d-%Y")
            except IndexError:
                deletion_date = False
                delete_date = False

            today_time = datetime.datetime.now().strftime('%m-%d-%Y')
            today_date = time.strptime(today_time, '%m-%d-%Y')

            # If image's DeleteOn date is less than or equal to today,
            # add this image to our list of images to process later
            if delete_date <= today_date:
                imagesList.append(image.id)

            # Make sure we have an AMI from today and mark backupSuccess as true
            if image.name.endswith(date_fmt):
                # Our latest backup from our other Lambda Function succeeded
                backupSuccess = True

    print("=============")

    print("About to process the following AMIs:")
    print(imagesList)

    if backupSuccess == True:

        snapshots = ec.describe_snapshots(MaxResults=1000, OwnerIds=[os.environ['ami_owner']])['Snapshots']

        # loop through list of image IDs
        for image in imagesList:
            print("deregistering image %s" % image)
            amiResponse = ec.deregister_image(
                DryRun=False,
                ImageId=image,
            )

            for snapshot in snapshots:
                if snapshot['Description'].find(image) > 0:
                    snap = ec.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                    print("Deleting snapshot " + snapshot['SnapshotId'])
                    print("-------------")

    else:
        print("No current backup found. Termination suspended.")
