terraform {
  required_version = ">= 1.1.9"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 4.14.0"
    }
  }
}

provider "aws" {
  region = var.region
}
