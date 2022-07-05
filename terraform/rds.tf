locals {
  db_subnet_group_name = "${var.project_prefix}_db_subnet_group_${var.environment}"
  db_name              = "${var.project_prefix}_db_${var.environment}"
}

resource "aws_db_subnet_group" "db_subnet_group" {
  name       = local.db_subnet_group_name
  subnet_ids = module.vpc.public_subnets
}

# resource "aws_db_instance" "db_instance" {
#   allocated_storage                     = "5"
#   identifier_prefix                     = var.project_prefix
#   db_name                               = local.db_name
#   db_subnet_group_name                  = aws_db_subnet_group.db_subnet_group.name
#   engine                                = "mysql"
#   engine_version                        = "8.0.28"
#   instance_class                        = "db.t2.micro"
#   iops                                  = "0"
#   license_model                         = "general-public-license"
#   multi_az                              = var.environment == "prod" ? "true" : "false"
#   option_group_name                     = "default:mysql-8-0"
#   parameter_group_name                  = "default.mysql8.0"
#   port                                  = "3306"
#   storage_encrypted                     = "false"
#   storage_type                          = "standard"
#   skip_final_snapshot                   = var.environment == "prod" ? "false" : "true"

#   username = "admin"
#   password = aws_secretsmanager_secret_version.password.secret_string

# }