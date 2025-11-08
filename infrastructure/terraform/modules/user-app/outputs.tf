# User App Module Outputs

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.user_app.name
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.user_app.id
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = aws_ecs_task_definition.user_app.arn
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.user_app.arn
}

output "target_group_name" {
  description = "Name of the target group"
  value       = aws_lb_target_group.user_app.name
}

output "listener_rule_arn" {
  description = "ARN of the ALB listener rule"
  value       = aws_lb_listener_rule.user_app.arn
}

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.user_app.name
}

output "endpoint_url" {
  description = "Full endpoint URL for the user app"
  value       = "http://${data.aws_lb.main.dns_name}/${var.path_prefix}"
}

output "alb_dns_name" {
  description = "DNS name of the ALB"
  value       = data.aws_lb.main.dns_name
}

output "path_pattern" {
  description = "Path pattern for routing to this app"
  value       = "/${var.path_prefix}/*"
}

output "app_info" {
  description = "Complete information about the deployed user app"
  value = {
    app_name           = var.app_name
    repository_url     = var.repository_url
    image_tag          = var.image_tag
    container_port     = var.container_port
    endpoint_url       = "http://${data.aws_lb.main.dns_name}/${var.path_prefix}"
    service_name       = aws_ecs_service.user_app.name
    target_group_arn   = aws_lb_target_group.user_app.arn
    log_group_name     = aws_cloudwatch_log_group.user_app.name
    path_pattern       = "/${var.path_prefix}/*"
    listener_priority  = var.listener_rule_priority
  }
}
