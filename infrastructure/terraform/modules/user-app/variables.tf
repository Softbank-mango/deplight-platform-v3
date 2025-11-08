# User App Module Variables

variable "app_name" {
  description = "Unique name for the user application (sanitized repo name with unique ID)"
  type        = string

  validation {
    condition     = length(var.app_name) <= 64 && can(regex("^[a-zA-Z0-9-]+$", var.app_name))
    error_message = "app_name must be 64 characters or less and contain only alphanumeric characters and hyphens"
  }
}

variable "repository_url" {
  description = "GitHub repository URL for the user app"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "ecr_repository_url" {
  description = "Full ECR repository URL (without tag)"
  type        = string
}

variable "container_port" {
  description = "Port on which the container listens"
  type        = number
  default     = 8000

  validation {
    condition     = var.container_port > 0 && var.container_port <= 65535
    error_message = "container_port must be between 1 and 65535"
  }
}

variable "container_cpu" {
  description = "CPU units for the container (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "256"

  validation {
    condition     = contains(["256", "512", "1024", "2048", "4096"], var.container_cpu)
    error_message = "container_cpu must be one of: 256, 512, 1024, 2048, 4096"
  }
}

variable "container_memory" {
  description = "Memory for the container in MiB (512, 1024, 2048, etc.)"
  type        = string
  default     = "512"
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 1

  validation {
    condition     = var.desired_count >= 0 && var.desired_count <= 10
    error_message = "desired_count must be between 0 and 10"
  }
}

variable "vpc_id" {
  description = "VPC ID where resources will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "assign_public_ip" {
  description = "Assign public IP to ECS tasks (required for public subnets)"
  type        = bool
  default     = true
}

variable "alb_name" {
  description = "Name of the existing Application Load Balancer"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the existing ECS cluster"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "ARN of the ECS execution role"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
}

variable "path_prefix" {
  description = "Path prefix for ALB routing (e.g., 'app/deployment-id')"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9/_-]+$", var.path_prefix))
    error_message = "path_prefix must contain only alphanumeric characters, hyphens, underscores, and forward slashes"
  }
}

variable "listener_rule_priority" {
  description = "Priority for the ALB listener rule (1-50000, lower = higher priority)"
  type        = number

  validation {
    condition     = var.listener_rule_priority >= 1 && var.listener_rule_priority <= 50000
    error_message = "listener_rule_priority must be between 1 and 50000"
  }
}

variable "health_check_path" {
  description = "Health check endpoint path"
  type        = string
  default     = "/"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "log_retention_days must be a valid CloudWatch Logs retention period"
  }
}

variable "environment_variables" {
  description = "Additional environment variables for the container"
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}
