# resource "random_password" "master" {
#   length           = 16
#   special          = true
#   override_special = "_!%^"
# }

# resource "aws_secretsmanager_secret" "password" {
#   name = local.secret_name

# }

# resource "aws_secretsmanager_secret_version" "password" {
#   secret_id     = aws_secretsmanager_secret.password.id
#   secret_string = random_password.master.result
# }

data "aws_secretsmanager_secret" "secrets" {
  arn = var.secret_arn
}

data "aws_secretsmanager_secret_version" "current" {
  secret_id = data.aws_secretsmanager_secret.secrets.id
}
