locals {
  application_name = "${var.project_prefix}-app-${var.environment}"
  environment_name = "${var.project_prefix}-env-${var.environment}"
  bot_token        = jsondecode(data.aws_secretsmanager_secret_version.current.secret_string)["bot_token"]
  db_password      = jsondecode(data.aws_secretsmanager_secret_version.current.secret_string)["db_password"]
}


resource "aws_elastic_beanstalk_application" "wb_bot_app" {
  name = local.application_name

  appversion_lifecycle {
    service_role          = "arn:aws:iam::737863547422:role/aws-elasticbeanstalk-service-role"
    max_count             = 128
    delete_source_from_s3 = true
  }
}

resource "aws_elastic_beanstalk_environment" "wb_bot_env" {
  application  = aws_elastic_beanstalk_application.wb_bot_app.name
  name         = local.environment_name
  platform_arn = "arn:aws:elasticbeanstalk:eu-central-1::platform/Python 3.8 running on 64bit Amazon Linux 2/3.3.15"
  tier         = "WebServer"

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = module.vpc.vpc_id
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = "aws-elasticbeanstalk-ec2-role"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "AssociatePublicIpAddress"
    value     = "True"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = join(",", module.vpc.public_subnets)
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "HasCoupledDatabase"
    value     = "true"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "MultiAZDatabase"
    value     = "false"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBAllocatedStorage"
    value     = "5"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBDeletionPolicy"
    value     = "Snapshot"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBEngine"
    value     = "mysql"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBEngineVersion"
    value     = ""
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBInstanceClass"
    value     = "db.t2.micro"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBUser"
    value     = "wbbot72qJhW"
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBPassword"
    # value     = aws_secretsmanager_secret_version.password.secret_string
    value = local.db_password
  }

  setting {
    namespace = "aws:rds:dbinstance"
    name      = "DBSnapshotIdentifier"
    value     = "cloningfordev"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "DBSubnets"
    value     = join(",", module.vpc.database_subnets)
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "MatcherHTTPCode"
    value     = "200"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "LoadBalancerType"
    value     = "application"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = "t2.micro"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBScheme"
    value     = "internet facing"
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MinSize"
    value     = 1
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MaxSize"
    value     = 2
  }

  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "SystemType"
    value     = "enhanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "BOT_TOKEN"
    value     = local.bot_token
  }

}
