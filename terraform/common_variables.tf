variable "environment" {
  type        = string
  description = "Environment type - develepment, testing, production etc."
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Value must be one of dev, prod."
  }
}

variable "aws_region" {
  type = string
}

# Secrets
variable "secret_arn" {
  type        = string
  description = "Secret ARN with sensative information."
}


# Prefixes
variable "project_prefix" {
  type        = string
  description = "AWS account prefix to be used for the given project."
}

# Tags
variable "common_tags" {
  type = map(string)
}