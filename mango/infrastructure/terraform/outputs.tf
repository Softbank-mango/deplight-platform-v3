# Outputs for Delightful Deploy

# ALB Outputs
output "alb_url" {
  description = "URL of the Application Load Balancer"
  value       = "http://${aws_lb.main.dns_name}"
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_test_url" {
  description = "Test URL for Green environment (port 8080)"
  value       = "http://${aws_lb.main.dns_name}:8080"
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "ecs_service_arn" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.app.id
}

output "ecs_task_definition" {
  description = "Latest ECS task definition"
  value       = aws_ecs_task_definition.app.arn
}

# Target Group Outputs
output "target_group_blue_arn" {
  description = "ARN of the Blue target group"
  value       = aws_lb_target_group.blue.arn
}

output "target_group_green_arn" {
  description = "ARN of the Green target group"
  value       = aws_lb_target_group.green.arn
}

# CodeDeploy Outputs
output "codedeploy_app_name" {
  description = "Name of the CodeDeploy application"
  value       = var.enable_blue_green_deployment ? aws_codedeploy_app.app[0].name : null
}

output "codedeploy_deployment_group" {
  description = "Name of the CodeDeploy deployment group"
  value       = var.enable_blue_green_deployment ? aws_codedeploy_deployment_group.app[0].deployment_group_name : null
}

output "codedeploy_artifacts_bucket" {
  description = "S3 bucket for CodeDeploy artifacts"
  value       = var.enable_blue_green_deployment ? aws_s3_bucket.codedeploy_artifacts[0].id : null
}

# Lambda Outputs
output "lambda_analyzer_arn" {
  description = "ARN of the AI Analyzer Lambda function"
  value       = aws_lambda_function.ai_analyzer.arn
}

output "lambda_analyzer_name" {
  description = "Name of the AI Analyzer Lambda function"
  value       = aws_lambda_function.ai_analyzer.function_name
}

output "lambda_function_url" {
  description = "Lambda Function URL for direct invocation"
  value       = aws_lambda_function_url.ai_analyzer.function_url
}

# DynamoDB Outputs
output "garden_state_table" {
  description = "Name of the Garden State DynamoDB table"
  value       = aws_dynamodb_table.garden_state.name
}

output "ai_analysis_table" {
  description = "Name of the AI Analysis DynamoDB table"
  value       = aws_dynamodb_table.ai_analysis.name
}

output "deployment_history_table" {
  description = "Name of the Deployment History DynamoDB table"
  value       = aws_dynamodb_table.deployment_history.name
}

# IAM Outputs
output "ecs_execution_role_arn" {
  description = "ARN of the ECS execution role"
  value       = var.use_existing_roles ? var.ecs_execution_role_arn : aws_iam_role.ecs_execution_role[0].arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = var.use_existing_roles ? var.ecs_task_role_arn : aws_iam_role.ecs_task_role[0].arn
}

# CloudWatch Outputs
output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = var.create_log_groups ? aws_cloudwatch_log_group.app[0].name : var.log_group_name_app
}

# Security Group Outputs
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "ID of the ECS tasks security group"
  value       = aws_security_group.ecs_tasks.id
}

# EventBridge Outputs REMOVED - No longer using EventBridge
# Lambda is invoked directly from GitHub Actions workflows

# SNS Outputs
output "sns_alerts_topic_arn" {
  description = "ARN of the SNS alerts topic"
  value       = aws_sns_topic.alerts.arn
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "vpc_id" {
  description = "VPC ID"
  value       = var.vpc_id
}

# Quick Start Commands
output "quick_start_commands" {
  description = "Quick start commands for using the infrastructure"
  value = {
    view_logs           = "aws logs tail ${var.create_log_groups ? aws_cloudwatch_log_group.app[0].name : var.log_group_name_app} --follow"
    view_dashboard      = "open https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
    describe_service    = "aws ecs describe-services --cluster ${aws_ecs_cluster.main.name} --services ${aws_ecs_service.app.name}"
    test_alb            = "curl http://${aws_lb.main.dns_name}/health"
    test_green          = "curl http://${aws_lb.main.dns_name}:8080/health"
    invoke_ai_analyzer  = "aws lambda invoke --function-name ${aws_lambda_function.ai_analyzer.function_name} /tmp/response.json"
    view_garden_state   = "aws dynamodb scan --table-name ${aws_dynamodb_table.garden_state.name} --max-items 10"
  }
}

# Deployment Information
output "deployment_info" {
  description = "Information about the current deployment"
  value = {
    image_tag              = var.image_tag
    commit_sha             = var.commit_sha
    container_port         = var.container_port
    desired_count          = var.desired_count
    deployment_config      = var.deployment_config_name
    health_check_path      = var.health_check_path
  }
}

# Garden UI Information
output "garden_ui_info" {
  description = "Information for Garden UI integration"
  value = {
    lambda_function_url    = aws_lambda_function_url.ai_analyzer.function_url
    garden_state_table     = aws_dynamodb_table.garden_state.name
    deployment_history     = aws_dynamodb_table.deployment_history.name
    alb_url                = "http://${aws_lb.main.dns_name}"
    cloudwatch_dashboard   = aws_cloudwatch_dashboard.main.dashboard_name
  }
}
