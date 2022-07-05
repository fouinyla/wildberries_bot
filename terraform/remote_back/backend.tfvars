aws_region = "eu-central-1"
# Prefixes
project_prefix = "wbbot"
# Terraform state
tf_bucket_state_name        = "terraform-state"
tf_dynamodb_state_lock_name = "terraform-state-lock"
# Tags
common_tags = {
  Project     = "wbbot"
  Application = "Wildberries Bot"
  Comment     = "Managed by Terraform"
}