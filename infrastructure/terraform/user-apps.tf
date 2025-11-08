# User Apps Infrastructure
# This file manages deployment of user applications (student projects)
# Each user app gets isolated infrastructure: ECS service, target group, ALB listener rule

# Local variables for user app configuration
locals {
  # Only create user app if deploy_user_app is true and required variables are provided
  create_user_app = var.deploy_user_app && var.user_app_name != "" && var.user_app_image != ""

  # Sanitize app name to ensure it meets AWS naming requirements
  # Remove special chars, convert to lowercase, limit length
  sanitized_app_name = local.create_user_app ? substr(
    replace(lower(var.user_app_name), "/[^a-z0-9-]/", "-"),
    0,
    60  # Leave room for suffixes
  ) : ""

  # Path prefix for ALB routing (e.g., "app/deployment-12345")
  user_app_path_prefix = local.create_user_app ? var.user_app_path_prefix : ""

  # Calculate next available priority for ALB listener rule
  # Platform uses: 40 (dashboard), 50 (api), 100 (health)
  # User apps start at priority 60 and increment
  # Priority is deterministic based on app name hash to avoid conflicts
  user_app_priority = local.create_user_app ? (
    60 + (abs(tonumber(substr(md5(local.sanitized_app_name), 0, 8), 16)) % 1000)
  ) : 0
}

# User App Module
module "user_app" {
  count  = local.create_user_app ? 1 : 0
  source = "./modules/user-app"

  # App identification
  app_name       = local.sanitized_app_name
  repository_url = var.user_app_repository_url

  # Container configuration
  image_tag         = var.user_app_image_tag
  ecr_repository_url = var.user_app_image  # Full image URL without tag
  container_port    = var.user_app_port
  container_cpu     = tostring(var.user_app_cpu)
  container_memory  = tostring(var.user_app_memory)
  desired_count     = var.user_app_desired_count

  # Network configuration
  vpc_id            = var.vpc_id
  subnet_ids        = var.public_subnet_ids  # Use public subnets with public IP
  security_group_id = aws_security_group.ecs_tasks.id
  assign_public_ip  = true

  # ALB configuration
  alb_name                = aws_lb.main.name
  ecs_cluster_name        = aws_ecs_cluster.main.name
  path_prefix             = local.user_app_path_prefix
  listener_rule_priority  = local.user_app_priority

  # IAM roles
  ecs_execution_role_arn = var.use_existing_roles ? var.ecs_execution_role_arn : aws_iam_role.ecs_execution_role[0].arn
  ecs_task_role_arn      = var.use_existing_roles ? var.ecs_task_role_arn : aws_iam_role.ecs_task_role[0].arn

  # Health check
  health_check_path = var.user_app_health_check_path

  # Logging
  log_retention_days = 7
  aws_region         = var.aws_region

  # Environment variables
  environment_variables = var.user_app_env_vars
}
