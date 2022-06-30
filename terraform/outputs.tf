output "aws_elastic_beanstalk_application_id" {
  value = aws_elastic_beanstalk_application.wb_bot_app.id
}

output "aws_elastic_beanstalk_environment_env_id" {
  value = aws_elastic_beanstalk_environment.wb_bot_env.id
}

# output "db_password" {
#   value = random_password.master.result
# }

output "env_endpoint_url" {
  value = aws_elastic_beanstalk_environment.wb_bot_env.endpoint_url
}