locals {
  pipeline_name = "${var.project_prefix}-pipeline-${var.environment}"
}

resource "aws_codepipeline" "wb_bot_pipeline" {
  name     = local.pipeline_name
  role_arn = "arn:aws:iam::737863547422:role/service-role/AWSCodePipelineServiceRole-eu-central-1-wb_pipeline"

  depends_on = [
    aws_elastic_beanstalk_application.wb_bot_app,
    aws_elastic_beanstalk_environment.wb_bot_env
  ]

  artifact_store {
    location = module.s3_artifacts_data.s3_bucket_id
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      output_artifacts = ["SourceArtifact"]
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      configuration = {
        FullRepositoryId = "fouinyla/wildberries_bot"
        BranchName       = "dev"
        ConnectionArn    = "arn:aws:codestar-connections:eu-central-1:737863547422:connection/fd22e2b8-5e32-4914-86fb-2d73e70ec1d8"
      }
    }
  }

  stage {
    name = "Deploy"
    action {
      category = "Deploy"

      configuration = {
        ApplicationName = local.application_name
        EnvironmentName = local.environment_name
      }

      input_artifacts = ["SourceArtifact"]
      name            = "Deploy"
      namespace       = "DeployVariables"
      owner           = "AWS"
      provider        = "ElasticBeanstalk"
      region          = "eu-central-1"
      version         = "1"
    }
  }
}