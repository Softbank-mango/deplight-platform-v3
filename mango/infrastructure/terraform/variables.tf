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
  default     = "/health"
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
