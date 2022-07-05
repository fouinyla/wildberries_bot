locals {
  s3_artifacts_name = "${var.project_prefix}-artifacts-${var.environment}"
}

module "s3_artifacts_data" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "3.3.0"

  bucket              = local.s3_artifacts_name
  acl                 = "private"
  block_public_policy = true
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
  versioning = {
    enabled = false
  }
}
