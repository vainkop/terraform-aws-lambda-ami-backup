terragrunt_version_constraint = ">= v0.37.0"
terraform_version_constraint  = ">= 1.1.9"

remote_state {
  backend = "s3"

  config = {
    encrypt        = true
    bucket         = "YOUR_STATE_S3_BUCKET_NAME_HERE"
    region         = "YOUR_REGION"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    acl            = "bucket-owner-full-control"
    dynamodb_table = "YOUR_LOCKS_DYNAMODB_NAME_HERE"
  }
}
