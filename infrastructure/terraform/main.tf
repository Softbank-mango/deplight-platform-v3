terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend Configuration
  # Choose one of the following:

  # Option 1: Local backend (default - uncommented)
  # State file will be stored locally in terraform.tfstate
  # Good for: Quick start, single developer, testing
  backend "local" {
    path = "terraform.tfstate"
  }

  # Option 2: Terraform Cloud (comment out local backend above and uncomment this)
  # State file managed remotely by Terraform Cloud
  # Good for: Team collaboration, state locking, remote operations
  # Prerequisites:
  #   1. Create account at https://app.terraform.io
  #   2. Create organization: delightful-deploy
  #   3. Create workspace: delightful-deploy-dev
  #   4. Set TF_API_TOKEN in GitHub Secrets
  #
  # cloud {
  #   organization = "delightful-deploy"
  #
  #   workspaces {
  #     name = "delightful-deploy-dev"
  #   }
  # }

  # Option 3: S3 backend (uncomment this and comment out local backend)
  # State file stored in S3 with DynamoDB locking
  # Good for: Team collaboration without Terraform Cloud
  #
  # backend "s3" {
  #   bucket         = "deplight-platform-tf-state"
  #   key            = "terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   encrypt        = true
  #   dynamodb_table = "deplight-platform-tf-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "DelightfulDeploy"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Hackathon   = "SoftBank2025"
    }
  }
}

# Data sources for existing resources
data "aws_caller_identity" "current" {}

data "aws_vpc" "main" {
  id = var.vpc_id
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:Type"
    values = ["public"]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:Type"
    values = ["private"]
  }
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name_prefix = "${var.app_name}-alb-"
  description = "Security group for ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP from internet"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS from internet"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.app_name}-alb-sg"
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${var.app_name}-ecs-tasks-"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow traffic from ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.app_name}-ecs-tasks-sg"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  count             = 1
  name              = var.log_group_name_app
  retention_in_days = 7

  tags = {
    Name = "${var.app_name}-logs"
  }
}
# S3 bucket for analyzer artifacts and deployment assets
resource "aws_s3_bucket" "artifacts" {
  count  = var.use_existing_artifacts_bucket ? 0 : 1
  bucket = "${var.app_name}-artifacts-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.app_name}-artifacts"
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  count  = var.use_existing_artifacts_bucket ? 0 : 1
  bucket = aws_s3_bucket.artifacts[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  count  = var.use_existing_artifacts_bucket ? 0 : 1
  bucket = aws_s3_bucket.artifacts[0].id

  rule {
    id     = "expire-old-artifacts"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
