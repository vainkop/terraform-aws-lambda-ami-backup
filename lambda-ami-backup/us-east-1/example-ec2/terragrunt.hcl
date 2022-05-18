include {
  path = find_in_parent_folders()
}

terraform {
  source = "../../..//modules/lambda-ami-backup"
}

locals { common_vars = yamldecode(file("values.yaml")) }

inputs = local.common_vars
