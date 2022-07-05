locals {
  vpc_name = "${var.project_prefix}_vpc_${var.environment}"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.14.2"

  name = local.vpc_name
  cidr = "10.0.0.0/16"

  azs              = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
  public_subnets   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  database_subnets = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  create_database_subnet_group           = true
  create_database_subnet_route_table     = true
  create_database_internet_gateway_route = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_nat_gateway = true
  enable_vpn_gateway = true
}