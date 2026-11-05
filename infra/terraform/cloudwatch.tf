# ==============================================================================
# Amazon CloudWatch Monitoring: Log Groups, Alarms, and Operational Dashboard
# AWS Resource: Amazon CloudWatch Centralized Observability & Telemetry.
# Free Tier Optimized: 14-day log retention cap (prevents indefinite storage accumulation).
# ==============================================================================

locals {
  monitored_lambdas = {
    create  = aws_lambda_function.create_incident
    get     = aws_lambda_function.get_incident
    list    = aws_lambda_function.list_incidents
    assign  = aws_lambda_function.assign_staff
    status  = aws_lambda_function.update_status
    resolve = aws_lambda_function.resolve_incident
    sla     = aws_lambda_function.check_sla
  }
}

# CloudWatch Log Group: Centralizes stdout/stderr execution logs per Lambda with a strict 14-day Free Tier retention.
resource "aws_cloudwatch_log_group" "lambda_logs" {
  for_each          = local.monitored_lambdas
  name              = "/aws/lambda/${each.value.function_name}"
  retention_in_days = 14 # Free Tier safety: prevents runaway storage billing from perpetual retention

  tags = {
    Name = "${var.project_name}-log-${each.key}"
  }
}

# CloudWatch Metric Alarm (Lambda Errors): Sends an automated SNS alert if any backend Lambda throws an unhandled exception.
resource "aws_cloudwatch_metric_alarm" "lambda_errors_alarm" {
  alarm_name          = "${var.project_name}-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300 # 5 minutes
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers when any CampusOps backend Lambda encounters an execution failure"
  alarm_actions       = [aws_sns_topic.admin_alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name = "${var.project_name}-lambda-errors-alarm"
  }
}

# CloudWatch Metric Alarm (API Gateway 5XX Errors): Alerts administrators if API Gateway encounters server-side 5XX errors.
resource "aws_cloudwatch_metric_alarm" "api_5xx_alarm" {
  alarm_name          = "${var.project_name}-api-5xx-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers when Amazon API Gateway returns a 5XX server failure to users"
  alarm_actions       = [aws_sns_topic.admin_alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiName = aws_api_gateway_rest_api.api.name
  }

  tags = {
    Name = "${var.project_name}-api-5xx-alarm"
  }
}

# CloudWatch Dashboard: Single-pane-of-glass operations console displaying API traffic, error rates, and Lambda latency.
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 2
        properties = {
          markdown = "# 🛡️ CampusOps Cloud-Native Operations Dashboard\nReal-time monitoring across API Gateway, Lambda serverless microservices, and DynamoDB storage."
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 2
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", aws_api_gateway_rest_api.api.name, { stat = "Sum", color = "#2563eb", label = "API Requests" }],
            [".", "4XXError", ".", ".", { stat = "Sum", color = "#f59e0b", label = "4XX Client Errors" }],
            [".", "5XXError", ".", ".", { stat = "Sum", color = "#dc2626", label = "5XX Server Errors" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Gateway Traffic & Error Status"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 2
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Latency", "ApiName", aws_api_gateway_rest_api.api.name, { stat = "Average", color = "#10b981", label = "Avg Latency (ms)" }],
            [".", "IntegrationLatency", ".", ".", { stat = "Average", color = "#8b5cf6", label = "Lambda Integration Latency (ms)" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API & Lambda Response Latency"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 8
        width  = 12
        height = 6
        properties = {
          metrics = [
            for k, fn in local.monitored_lambdas : [
              "AWS/Lambda", "Invocations", "FunctionName", fn.function_name, { stat = "Sum" }
            ]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.aws_region
          title   = "Lambda Invocations by Microservice"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 8
        width  = 12
        height = 6
        properties = {
          metrics = [
            for k, fn in local.monitored_lambdas : [
              "AWS/Lambda", "Errors", "FunctionName", fn.function_name, { stat = "Sum", color = "#dc2626" }
            ]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Failures & Exceptions"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 14
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.incidents.name, { stat = "Sum", color = "#0284c7", label = "DynamoDB Consumed RCU" }],
            [".", "ConsumedWriteCapacityUnits", ".", ".", { stat = "Sum", color = "#16a34a", label = "DynamoDB Consumed WCU" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "DynamoDB Storage Throughput (On-Demand RCUs/WCUs)"
          period  = 300
        }
      }
    ]
  })
}

