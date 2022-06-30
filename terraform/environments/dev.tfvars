environment = "dev"
aws_region  = "eu-central-1"
# Prefixes
project_prefix = "wbbot"
# Secrets
secret_arn = "arn:aws:secretsmanager:eu-central-1:737863547422:secret:wbbot_dev-MwcG0e"
# Tags
common_tags = {
  Project     = "wbbot"
  Application = "Wildberries Bot"
  Environment = "Development"
  Comment     = "Managed by Terraform"
}