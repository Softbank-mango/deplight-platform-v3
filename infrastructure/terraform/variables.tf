variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "delightful-deploy"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
  default     = "vpc-0139379503d38f151"
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for ALB"
  type        = list(string)
  default = [
    "subnet-08910097cf5286210",  # ap-northeast-2b (same as ECS tasks)
    "subnet-067bccb68d144573b"   # ap-northeast-2c (same as ECS tasks)
  ]
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks"
  type        = list(string)
  default = [
    "subnet-08910097cf5286210",  # ap-northeast-2b
    "subnet-067bccb68d144573b"   # ap-northeast-2c
  ]
}

variable "container_port" {
  description = "Port on which the container listens"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "CPU units for the container (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory for the container in MiB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 2
}

variable "min_capacity" {
  description = "Minimum number of tasks for autoscaling"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of tasks for autoscaling"
  type        = number
  default     = 4
}

variable "ecr_repository_url" {
  description = "ECR repository URL"
  type        = string
  default     = "513348493870.dkr.ecr.ap-northeast-2.amazonaws.com/delightful-deploy"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "commit_sha" {
  description = "Git commit SHA"
  type        = string
  default     = "unknown"
}

variable "health_check_path" {
  description = "Health check endpoint path"
  type        = string
  default     = "/api/health"
}

variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "health_check_healthy_threshold" {
  description = "Number of consecutive health checks for healthy status"
  type        = number
  default     = 2
}

variable "health_check_unhealthy_threshold" {
  description = "Number of consecutive health checks for unhealthy status"
  type        = number
  default     = 3
}

variable "deregistration_delay" {
  description = "Time to wait before deregistering a target"
  type        = number
  default     = 30
}

variable "letsur_api_key_param" {
  description = "SSM parameter name for Letsur API key"
  type        = string
  default     = "/delightful/letsur/api_key"
}

variable "letsur_base_url" {
  description = "Letsur API base URL"
  type        = string
  default     = "https://gateway.letsur.ai/v1"
}

variable "letsur_model" {
  description = "Letsur model name"
  type        = string
  default     = "gpt-5"
}

variable "enable_blue_green_deployment" {
  description = "Enable Blue-Green deployment with CodeDeploy (10-15min, safest). False = ECS Circuit Breaker (1-2min, production-safe)"
  type        = bool
  default     = false  # Fast mode: 1-2 minute deployments with AI + Circuit Breaker
}

variable "deployment_config_name" {
  description = "CodeDeploy deployment configuration"
  type        = string
  default     = "CodeDeployDefault.ECSCanary10Percent5Minutes"
}

variable "termination_wait_time" {
  description = "Time to wait before terminating original task set (minutes)"
  type        = number
  default     = 5
}

variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights"
  type        = bool
  default     = true
}

variable "enable_xray" {
  description = "Enable AWS X-Ray tracing"
  type        = bool
  default     = true
}

variable "create_vpc_endpoints" {
  description = "Create VPC interface endpoints for SSM/ECR/Logs. Disable if endpoints or conflicting private DNS already exist in the VPC."
  type        = bool
  default     = false
}

variable "route_table_ids" {
  description = "List of route table IDs for Gateway VPC endpoints (S3, DynamoDB)"
  type        = list(string)
  default     = []
}

# Optional controls to integrate with existing environment
variable "use_existing_roles" {
  description = "Use pre-existing IAM roles instead of creating new ones"
  type        = bool
  default     = true
}

variable "ecs_execution_role_arn" {
  description = "Existing ECS execution role ARN (required if use_existing_roles=true)"
  type        = string
  default     = "arn:aws:iam::513348493870:role/delightful-deploy-ecs-execution-role"
}

variable "ecs_task_role_arn" {
  description = "Existing ECS task role ARN (required if use_existing_roles=true)"
  type        = string
  default     = "arn:aws:iam::513348493870:role/delightful-deploy-ecs-task-role"
}

variable "lambda_analyzer_role_arn" {
  description = "Existing Lambda analyzer role ARN (required if use_existing_roles=true)"
  type        = string
  default     = "arn:aws:iam::513348493870:role/delightful-deploy-lambda-analyzer-role"
}

variable "create_log_groups" {
  description = "Create CloudWatch log groups for ECS tasks and Lambda functions"
  type        = bool
  default     = true  # Changed to true to let Terraform manage log groups
}

variable "log_group_name_app" {
  description = "CloudWatch log group name for app"
  type        = string
  default     = "/aws/ecs/delightful-deploy"
}

variable "log_group_name_dashboard" {
  description = "CloudWatch log group name for dashboard"
  type        = string
  default     = "/aws/ecs/delightful-deploy-dashboard"
}

variable "log_group_name_lambda" {
  description = "CloudWatch log group name for Lambda"
  type        = string
  default     = "/aws/lambda/delightful-deploy-ai-analyzer"
}

variable "use_existing_artifacts_bucket" {
  description = "Use pre-existing S3 artifacts bucket"
  type        = bool
  default     = true
}

variable "artifacts_bucket_name" {
  description = "Artifacts bucket name (used if use_existing_artifacts_bucket=true)"
  type        = string
  default     = "deplight-platform-artifacts-apne2"
}

variable "cpu_target_value" {
  description = "Target CPU utilization for autoscaling"
  type        = number
  default     = 70
}

variable "memory_target_value" {
  description = "Target memory utilization for autoscaling"
  type        = number
  default     = 80
}

variable "slack_webhook_url_param" {
  description = "SSM parameter name for Slack webhook URL"
  type        = string
  default     = "/delightful/slack/webhook_url"
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

# =====================================================
# User App Deployment Variables (Multi-tenant support)
# =====================================================

variable "deploy_user_app" {
  description = "Whether to deploy a user application (student project)"
  type        = bool
  default     = false
}

variable "user_app_name" {
  description = "User application name (sanitized repo name or deployment ID)"
  type        = string
  default     = ""
}

variable "user_app_repository_url" {
  description = "GitHub repository URL for the user application"
  type        = string
  default     = ""
}

variable "user_app_image" {
  description = "Full ECR repository URL for user app (without tag)"
  type        = string
  default     = ""
}

variable "user_app_image_tag" {
  description = "Docker image tag for user app"
  type        = string
  default     = "latest"
}

variable "user_app_port" {
  description = "Container port for user app"
  type        = number
  default     = 8000
}

variable "user_app_cpu" {
  description = "CPU units for user app container (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "user_app_memory" {
  description = "Memory in MiB for user app container (512, 1024, 2048, etc.)"
  type        = number
  default     = 512
}

variable "user_app_desired_count" {
  description = "Desired number of tasks for user app"
  type        = number
  default     = 1
}

variable "user_app_path_prefix" {
  description = "Path prefix for ALB routing (e.g., 'app/deployment-id')"
  type        = string
  default     = ""
}

variable "user_app_health_check_path" {
  description = "Health check path for user app"
  type        = string
  default     = "/"
}

variable "user_app_env_vars" {
  description = "Additional environment variables for user app"
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

# Names for existing shared resources used by user apps (to avoid rooting into platform resources)
variable "user_app_alb_name" {
  description = "Name of the existing ALB to attach user app routes"
  type        = string
  default     = "delightful-deploy-alb"
}

variable "user_app_ecs_cluster_name" {
  description = "Name of the existing ECS cluster where user apps run"
  type        = string
  default     = "delightful-deploy-cluster"
}

variable "user_app_security_group_id" {
  description = "Security group ID for user app ECS tasks"
  type        = string
  default     = ""
}
