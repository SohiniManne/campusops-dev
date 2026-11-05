# ==============================================================================
# Amazon EventBridge Scheduled SLA Monitoring Automation
# AWS Resource: Amazon EventBridge Rule and Lambda Event Target.
# ==============================================================================

# EventBridge Schedule Rule: Serverless cron scheduler that triggers the overdue SLA check every 10 minutes.
resource "aws_cloudwatch_event_rule" "sla_schedule" {
  name                = "${var.project_name}-sla-cron-${var.environment}"
  description         = "Triggers check_sla Lambda periodically to detect overdue campus incidents"
  schedule_expression = "rate(10 minutes)" # 100% Free Tier: EventBridge rule triggers are free

  tags = {
    Name = "${var.project_name}-sla-cron"
  }
}

# EventBridge Target: Connects the 10-minute scheduled rule to the check_sla Lambda function.
resource "aws_cloudwatch_event_target" "check_sla_target" {
  rule      = aws_cloudwatch_event_rule.sla_schedule.name
  target_id = "CheckSLALambdaTarget"
  arn       = aws_lambda_function.check_sla.arn
}

# Lambda Permission: Permits Amazon EventBridge service to trigger the check_sla Lambda execution.
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.check_sla.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sla_schedule.arn
}

