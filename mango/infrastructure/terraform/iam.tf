# ECS Task Execution Role
resource "aws_iam_role" "ecs_execution_role" {
  count = var.use_existing_roles ? 0 : 1
  name = "${var.app_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.app_name}-ecs-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  count      = var.use_existing_roles ? 0 : 1
  role       = aws_iam_role.ecs_execution_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for SSM Parameter Store access (for secrets)
resource "aws_iam_role_policy" "ecs_execution_ssm_policy" {
  count = var.use_existing_roles ? 0 : 1
  name  = "${var.app_name}-ecs-execution-ssm-policy"
  role  = aws_iam_role.ecs_execution_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter${var.letsur_api_key_param}",
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter${var.slack_webhook_url_param}"
        ]
      }
    ]
  })
}

# ECS Task Role (for application runtime permissions)
resource "aws_iam_role" "ecs_task_role" {
  count = var.use_existing_roles ? 0 : 1
  name = "${var.app_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.app_name}-ecs-task-role"
  }
}

# Task role policies for X-Ray, CloudWatch, DynamoDB
resource "aws_iam_role_policy" "ecs_task_policy" {
  count = var.use_existing_roles ? 0 : 1
  name = "${var.app_name}-ecs-task-policy"
  role = aws_iam_role.ecs_task_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/ecs/${var.app_name}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.garden_state.arn,
          "${aws_dynamodb_table.garden_state.arn}/index/*",
          aws_dynamodb_table.deployment_logs.arn,
          "${aws_dynamodb_table.deployment_logs.arn}/index/*",
          aws_dynamodb_table.ai_analysis.arn,
          aws_dynamodb_table.deployment_history.arn
        ]
      }
    ]
  })
}

# CodeDeploy Service Role
resource "aws_iam_role" "codedeploy" {
  count = var.enable_blue_green_deployment ? 1 : 0
  name  = "${var.app_name}-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.app_name}-codedeploy-role"
  }
}

resource "aws_iam_role_policy_attachment" "codedeploy_policy" {
  count      = var.enable_blue_green_deployment ? 1 : 0
  role       = aws_iam_role.codedeploy[0].name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployRoleForECS"
}

# Lambda Execution Role for AI Analyzer
resource "aws_iam_role" "lambda_analyzer" {
  count = var.use_existing_roles ? 0 : 1
  name = "${var.app_name}-lambda-analyzer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.app_name}-lambda-analyzer-role"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  count      = var.use_existing_roles ? 0 : 1
  role       = aws_iam_role.lambda_analyzer[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_analyzer_policy" {
  count = var.use_existing_roles ? 0 : 1
  name = "${var.app_name}-lambda-analyzer-policy"
  role = aws_iam_role.lambda_analyzer[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter${var.letsur_api_key_param}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.garden_state.arn,
          aws_dynamodb_table.ai_analysis.arn,
          aws_dynamodb_table.deployment_history.arn,
          aws_dynamodb_table.deployment_logs.arn,
          "${aws_dynamodb_table.deployment_logs.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::${var.app_name}-artifacts-*/*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:DescribeImages"
        ]
        Resource = "*"
      }
    ]
  })
}

# EventBridge IAM resources REMOVED - No longer using EventBridge
# Lambda is invoked directly from GitHub Actions with AWS credentials
