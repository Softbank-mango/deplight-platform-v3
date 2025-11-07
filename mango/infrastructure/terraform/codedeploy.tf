# CodeDeploy Application
resource "aws_codedeploy_app" "app" {
  count            = var.enable_blue_green_deployment ? 1 : 0
  name             = "${var.app_name}-app"
  compute_platform = "ECS"

  tags = {
    Name = "${var.app_name}-codedeploy-app"
  }
}

# CodeDeploy Deployment Group
resource "aws_codedeploy_deployment_group" "app" {
  count                  = var.enable_blue_green_deployment ? 1 : 0
  app_name               = aws_codedeploy_app.app[0].name
  deployment_group_name  = "${var.app_name}-dg"
  service_role_arn       = aws_iam_role.codedeploy[0].arn
  deployment_config_name = var.deployment_config_name

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
  }

  blue_green_deployment_config {
    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = var.termination_wait_time
    }

    deployment_ready_option {
      action_on_timeout = "CONTINUE_DEPLOYMENT"
    }
  }

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  ecs_service {
    cluster_name = aws_ecs_cluster.main.name
    service_name = aws_ecs_service.app.name
  }

  load_balancer_info {
    target_group_pair_info {
      prod_traffic_route {
        listener_arns = [aws_lb_listener.http.arn]
      }

      test_traffic_route {
        listener_arns = [aws_lb_listener.http_test.arn]
      }

      target_group {
        name = aws_lb_target_group.blue.name
      }

      target_group {
        name = aws_lb_target_group.green.name
      }
    }
  }

  # Optional: CloudWatch alarms to trigger automatic rollback
  dynamic "alarm_configuration" {
    for_each = length(aws_cloudwatch_metric_alarm.alb_5xx_errors) > 0 ? [1] : []
    content {
      enabled = true
      alarms = [
        aws_cloudwatch_metric_alarm.alb_5xx_errors.alarm_name,
        aws_cloudwatch_metric_alarm.alb_healthy_hosts.alarm_name
      ]
    }
  }

  tags = {
    Name = "${var.app_name}-deployment-group"
  }
}

# S3 Bucket for CodeDeploy artifacts (appspec.yaml, scripts)
resource "aws_s3_bucket" "codedeploy_artifacts" {
  count  = var.enable_blue_green_deployment ? 1 : 0
  bucket = "${var.app_name}-codedeploy-artifacts-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.app_name}-codedeploy-artifacts"
  }
}

resource "aws_s3_bucket_versioning" "codedeploy_artifacts" {
  count  = var.enable_blue_green_deployment ? 1 : 0
  bucket = aws_s3_bucket.codedeploy_artifacts[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "codedeploy_artifacts" {
  count  = var.enable_blue_green_deployment ? 1 : 0
  bucket = aws_s3_bucket.codedeploy_artifacts[0].id

  rule {
    id     = "expire-old-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# AppSpec template for ECS Blue-Green deployment
resource "local_file" "appspec_template" {
  count    = var.enable_blue_green_deployment ? 1 : 0
  filename = "${path.module}/../appspec.yaml"

  content = yamlencode({
    version = "0.0"
    Resources = [
      {
        TargetService = {
          Type = "AWS::ECS::Service"
          Properties = {
            TaskDefinition = "<TASK_DEFINITION>"
            LoadBalancerInfo = {
              ContainerName = var.app_name
              ContainerPort = var.container_port
            }
            PlatformVersion = "LATEST"
          }
        }
      }
    ]
    Hooks = [
      {
        BeforeInstall = "BeforeInstall"
      },
      {
        AfterInstall = "AfterInstall"
      },
      {
        AfterAllowTestTraffic = "AfterAllowTestTraffic"
      },
      {
        BeforeAllowTraffic = "BeforeAllowTraffic"
      },
      {
        AfterAllowTraffic = "AfterAllowTraffic"
      }
    ]
  })
}

# Lambda functions for deployment lifecycle hooks (optional but recommended)
resource "aws_lambda_function" "deployment_hook_before_allow_traffic" {
  count         = var.enable_blue_green_deployment ? 1 : 0
  function_name = "${var.app_name}-before-allow-traffic"
  role          = var.use_existing_roles ? var.lambda_analyzer_role_arn : aws_iam_role.lambda_analyzer[0].arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30

  filename         = "${path.module}/../build/deployment_hooks.zip"
  source_code_hash = fileexists("${path.module}/../build/deployment_hooks.zip") ? filebase64sha256("${path.module}/../build/deployment_hooks.zip") : null

  environment {
    variables = {
      DEPLOYMENT_ID = aws_codedeploy_deployment_group.app[0].deployment_group_name
      ENVIRONMENT   = var.environment
    }
  }

  tags = {
    Name = "${var.app_name}-before-allow-traffic-hook"
  }
}

resource "aws_lambda_function" "deployment_hook_after_allow_traffic" {
  count         = var.enable_blue_green_deployment ? 1 : 0
  function_name = "${var.app_name}-after-allow-traffic"
  role          = var.use_existing_roles ? var.lambda_analyzer_role_arn : aws_iam_role.lambda_analyzer[0].arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30

  filename         = "${path.module}/../build/deployment_hooks.zip"
  source_code_hash = fileexists("${path.module}/../build/deployment_hooks.zip") ? filebase64sha256("${path.module}/../build/deployment_hooks.zip") : null

  environment {
    variables = {
      DEPLOYMENT_ID = aws_codedeploy_deployment_group.app[0].deployment_group_name
      ENVIRONMENT   = var.environment
    }
  }

  tags = {
    Name = "${var.app_name}-after-allow-traffic-hook"
  }
}
