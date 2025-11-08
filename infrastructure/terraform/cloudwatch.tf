# CloudWatch Dashboard for Deployment Garden
locals {
  app_log_group_name = var.create_log_groups ? aws_cloudwatch_log_group.app[0].name : var.log_group_name_app
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.app_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      # Row 1: Service Health Overview
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average", color = "#1f77b4" }],
            [".", "MemoryUtilization", { stat = "Average", color = "#ff7f0e" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ECS Service Metrics"
          period  = 300
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", { stat = "Average" }],
            [".", "RequestCount", { stat = "Sum", yAxis = "right" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ALB Performance"
          period  = 300
          yAxis = {
            left = {
              label = "Response Time (s)"
            }
            right = {
              label = "Request Count"
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", { stat = "Average", color = "#2ca02c" }],
            [".", "UnHealthyHostCount", { stat = "Average", color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Target Health"
          period  = 60
        }
      },

      # Row 2: Error Rates
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", { stat = "Sum", color = "#ff7f0e" }],
            [".", "HTTPCode_Target_5XX_Count", { stat = "Sum", color = "#d62728" }],
            [".", "HTTPCode_ELB_5XX_Count", { stat = "Sum", color = "#9467bd" }]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.aws_region
          title   = "Error Rates"
          period  = 300
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum", color = "#1f77b4" }],
            [".", "Errors", { stat = "Sum", color = "#d62728" }],
            [".", "Throttles", { stat = "Sum", color = "#ff7f0e" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda AI Analyzer Metrics"
          period  = 300
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", { stat = "Average" }],
            ["...", { stat = "p99", label = "p99 Duration" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Duration"
          period  = 300
          yAxis = {
            left = {
              label = "Duration (ms)"
            }
          }
        }
      },

      # Row 3: Deployment Garden State
      {
        type = "log"
        properties = {
          query   = "SOURCE '${local.app_log_group_name}' | fields @timestamp, @message | filter @message like /deployment/ | sort @timestamp desc | limit 20"
          region  = var.aws_region
          title   = "Recent Deployments"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.app_name}", "DeploymentSuccess", { stat = "Sum", color = "#2ca02c" }],
            [".", "DeploymentFailure", { stat = "Sum", color = "#d62728" }]
          ]
          view    = "singleValue"
          region  = var.aws_region
          title   = "Deployment Success Rate (24h)"
          period  = 86400
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.app_name}", "GardenFlowers", { stat = "Maximum", color = "#2ca02c" }]
          ]
          view    = "singleValue"
          region  = var.aws_region
          title   = "Garden Flowers (Successful Deploys)"
          period  = 2592000  # 30 days
        }
      }
    ]
  })
}

# Custom Metrics for Deployment Garden
resource "aws_cloudwatch_log_metric_filter" "deployment_success" {
  count          = var.create_log_groups ? 1 : 0
  name           = "${var.app_name}-deployment-success"
  log_group_name = local.app_log_group_name
  pattern        = "[timestamp, request_id, event_type = DEPLOYMENT_SUCCESS, ...]"

  metric_transformation {
    name      = "DeploymentSuccess"
    namespace = var.app_name
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_log_metric_filter" "deployment_failure" {
  count          = var.create_log_groups ? 1 : 0
  name           = "${var.app_name}-deployment-failure"
  log_group_name = local.app_log_group_name
  pattern        = "[timestamp, request_id, event_type = DEPLOYMENT_FAILURE, ...]"

  metric_transformation {
    name      = "DeploymentFailure"
    namespace = var.app_name
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_log_metric_filter" "garden_flowers" {
  count          = var.create_log_groups ? 1 : 0
  name           = "${var.app_name}-garden-flowers"
  log_group_name = local.app_log_group_name
  pattern        = "[timestamp, request_id, event_type = BLOOM, ...]"

  metric_transformation {
    name      = "GardenFlowers"
    namespace = var.app_name
    value     = "1"
    unit      = "Count"
  }
}

# Composite Alarm for Critical Service Health
resource "aws_cloudwatch_composite_alarm" "service_critical" {
  alarm_name          = "${var.app_name}-service-critical"
  alarm_description   = "Composite alarm for critical service health issues"
  actions_enabled     = true
  alarm_actions       = []

  alarm_rule = "ALARM(${aws_cloudwatch_metric_alarm.alb_healthy_hosts.alarm_name}) OR ALARM(${aws_cloudwatch_metric_alarm.alb_5xx_errors.alarm_name})"

  tags = {
    Name     = "${var.app_name}-service-critical-alarm"
    Severity = "Critical"
  }
}

# SNS Topic for Alerts (optional - can integrate with Slack)
resource "aws_sns_topic" "alerts" {
  name = "${var.app_name}-alerts"

  tags = {
    Name = "${var.app_name}-alerts"
  }
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count     = 0  # Set to 1 and provide email to enable
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "your-email@example.com"  # Replace with actual email
}

# CloudWatch Insights Queries
resource "aws_cloudwatch_query_definition" "error_analysis" {
  name = "${var.app_name}-error-analysis"

  log_group_names = concat(
    [local.app_log_group_name],
    var.create_log_groups ? [aws_cloudwatch_log_group.lambda_analyzer[0].name] : [var.log_group_name_lambda]
  )

  query_string = <<-QUERY
    fields @timestamp, @message
    | filter @message like /ERROR/
    | parse @message /(?<error_type>\w+Error):/
    | stats count() by error_type
    | sort count() desc
  QUERY
}

resource "aws_cloudwatch_query_definition" "deployment_timeline" {
  name = "${var.app_name}-deployment-timeline"

  log_group_names = [
    local.app_log_group_name
  ]

  query_string = <<-QUERY
    fields @timestamp, @message
    | filter @message like /DEPLOYMENT/
    | sort @timestamp desc
    | limit 50
  QUERY
}

resource "aws_cloudwatch_query_definition" "performance_analysis" {
  name = "${var.app_name}-performance-analysis"

  log_group_names = [
    local.app_log_group_name
  ]

  query_string = <<-QUERY
    fields @timestamp, @message
    | filter @type = "REPORT"
    | parse @message /Duration: (?<duration>\d+\.\d+)/
    | parse @message /Billed Duration: (?<billed_duration>\d+)/
    | parse @message /Memory Size: (?<memory_size>\d+)/
    | parse @message /Max Memory Used: (?<memory_used>\d+)/
    | stats avg(duration), max(duration), avg(memory_used), max(memory_used) by bin(5m)
  QUERY
}

# X-Ray Sampling Rule (if X-Ray is enabled)
resource "aws_xray_sampling_rule" "main" {
  count = var.enable_xray ? 1 : 0

  rule_name      = "${var.app_name}-sampling-rule"
  priority       = 1000
  version        = 1
  reservoir_size = 1
  fixed_rate     = 0.05
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = var.app_name
  resource_arn   = "*"

  attributes = {
    Environment = var.environment
  }
}
