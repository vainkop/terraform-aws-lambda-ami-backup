# Automated AMI Backups
#
# @author Valerii Vainkop <vainkop@gmail.com>
#
# "retention_days" is environment variable which will be used as a retention policy number in days. If there is no
# environment variable with that name, it will use a 60 days default value for each AMI.
#
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function


import boto3
import collections
import datetime
import sys
import pprint
import os
import json

ec = boto3.client('ec2')
ec2_instance_id = os.environ['instance_id']
ec2_instance_name = os.environ['name']
label_id = os.environ['label_id']
no_reboot = os.environ['reboot'] == '0'
block_device_mappings = json.loads(str(os.environ['block_device_mappings']))

def lambda_handler(event, context):
    try:
        retention_days = int(os.environ['retention'])
    except ValueError:
        retention_days = 60

    create_time = datetime.datetime.now()
    create_fmt = create_time.strftime('%Y-%m-%d')

    delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
    delete_fmt = delete_date.strftime('%m-%d-%Y')

    name_tag = ec2_instance_name + "-" + create_fmt + "-" + ec2_instance_id

    AMIid = ec.create_image(InstanceId=ec2_instance_id,
                            Name=label_id + "-" + ec2_instance_id + "-" + create_fmt,
                            Description=label_id + "-" + ec2_instance_id + "-" + create_fmt,
                            NoReboot=no_reboot, DryRun=False,
                            BlockDeviceMappings=block_device_mappings,
                            TagSpecifications=[
                              {
                                'ResourceType': 'snapshot',
                                'Tags': [
                                  {
                                     'Key': 'Name',
                                     'Value': name_tag
                                  },
                                  {
                                    'Key': 'DeleteOn',
                                    'Value': delete_fmt
                                  }
                                ]
                              },
                              {
                                'ResourceType': 'image',
                                'Tags': [
                                  {
                                     'Key': 'Name',
                                     'Value': name_tag
                                  },
                                  {
                                    'Key': 'DeleteOn',
                                    'Value': delete_fmt
                                  }
                                ]
                              }
                            ])

    print("Retaining AMI %s of instance %s for %d days" % (
        AMIid['ImageId'],
        ec2_instance_id,
        retention_days,
    ))
