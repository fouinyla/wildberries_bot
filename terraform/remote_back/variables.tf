variable "aws_region" {
  type = string
}

# Prefixes
variable "project_prefix" {
  type        = string
  description = "AWS account prefix to be used for the given project."
}

# Terraform state
variable "tf_bucket_state_name" {
  type        = string
  description = "S3 Bucket name for Terraform state."
}

variable "tf_dynamodb_state_lock_name" {
  type        = string
  description = "DynamoDB table name for lock Terraform state."
}

# Tags
variable "common_tags" {
  type = map(string)
}