# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  tags = {
    Name = "${var.app_name}-cluster"
  }
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 1
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = var.use_existing_roles ? var.ecs_execution_role_arn : aws_iam_role.ecs_execution_role[0].arn
  task_role_arn            = var.use_existing_roles ? var.ecs_task_role_arn : aws_iam_role.ecs_task_role[0].arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = "${var.ecr_repository_url}:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "PORT"
          value = tostring(var.container_port)
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "COMMIT_SHA"
          value = var.commit_sha
        }
      ]

      secrets = [
        {
          name      = "LETSUR_API_KEY"
          valueFrom = var.letsur_api_key_param
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_name_app
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}${var.health_check_path} || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      linuxParameters = var.enable_xray ? {
        initProcessEnabled = true
      } : null
    }
  ])

  # Add X-Ray sidecar if enabled

  tags = {
    Name      = "${var.app_name}-task-def"
    CommitSHA = var.commit_sha
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  # Use Blue-Green deployment if enabled
  deployment_controller {
    type = var.enable_blue_green_deployment ? "CODE_DEPLOY" : "ECS"
  }

  # Circuit Breaker and deployment configuration (when not using CodeDeploy)
  dynamic "deployment_circuit_breaker" {
    for_each = var.enable_blue_green_deployment ? [] : [1]
    content {
      enable   = true
      rollback = true
    }
  }

  # Deployment configuration
  deployment_minimum_healthy_percent = var.enable_blue_green_deployment ? 100 : 100
  deployment_maximum_percent         = var.enable_blue_green_deployment ? 100 : 200

  # Load balancer configuration
  dynamic "load_balancer" {
    for_each = var.enable_blue_green_deployment ? [1] : []
    content {
      target_group_arn = aws_lb_target_group.blue.arn
      container_name   = var.app_name
      container_port   = var.container_port
    }
  }

  dynamic "load_balancer" {
    for_each = var.enable_blue_green_deployment ? [] : [1]
    content {
      target_group_arn = aws_lb_target_group.blue.arn
      container_name   = var.app_name
      container_port   = var.container_port
    }
  }

  # Enable CloudWatch Container Insights
  enable_ecs_managed_tags = true
  propagate_tags          = "SERVICE"

  # Ignore task definition changes when using Blue-Green
  lifecycle {
    ignore_changes = [
      task_definition,
      load_balancer,
    ]
  }

  depends_on = [
    aws_lb_listener.http,
    aws_iam_role_policy_attachment.ecs_execution_role_policy
  ]

  tags = {
    Name = "${var.app_name}-service"
  }
}

# =====================
# Dashboard ECS Service
# =====================

resource "aws_cloudwatch_log_group" "dashboard" {
  count             = 1
  name              = "/aws/ecs/${var.app_name}-dashboard"
  retention_in_days = 7

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_ecs_task_definition" "dashboard" {
  family                   = "${var.app_name}-dashboard"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = var.use_existing_roles ? var.ecs_execution_role_arn : aws_iam_role.ecs_execution_role[0].arn
  task_role_arn            = var.use_existing_roles ? var.ecs_task_role_arn : aws_iam_role.ecs_task_role[0].arn

  container_definitions = jsonencode([
    {
      name      = "dashboard"
      image     = "${var.ecr_repository_url}:dashboard-latest"
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "PORT", value = tostring(var.container_port) },
        { name = "ENVIRONMENT", value = var.environment },
        { name = "ALB_DNS", value = aws_lb.main.dns_name },
        { name = "AWS_REGION", value = var.aws_region }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_name_dashboard
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "dashboard" {
  name            = "${var.app_name}-dashboard-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  deployment_controller {
    type = "ECS"
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.dashboard.arn
    container_name   = "dashboard"
    container_port   = var.container_port
  }

  enable_ecs_managed_tags = true
  propagate_tags          = "SERVICE"

  depends_on = [
    aws_lb_listener.http
  ]
}

# Auto Scaling Target
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.app_name}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = var.cpu_target_value
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto Scaling Policy - Memory
resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.app_name}-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = var.memory_target_value
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
