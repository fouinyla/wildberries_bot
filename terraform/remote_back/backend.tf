provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.common_tags
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.19.0"
    }
  }
}

locals {
  tf_bucket_state_full_name        = "${var.project_prefix}-${var.tf_bucket_state_name}"
  tf_dynamodb_state_lock_full_name = "${var.project_prefix}-${var.tf_dynamodb_state_lock_name}"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = local.tf_bucket_state_full_name
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name         = local.tf_dynamodb_state_lock_full_name
  hash_key     = "LockID"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "LockID"
    type = "S"
  }
}

