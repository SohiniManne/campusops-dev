# ==============================================================================
# Amazon SNS Topic & Admin Email Alerts for SLA Escalations
# AWS Resource: Amazon Simple Notification Service (SNS) Topic and Subscriptions.
# ==============================================================================

# SNS Topic: Pub/Sub messaging channel that receives automated escalation alerts for breached incidents.
resource "aws_sns_topic" "admin_alerts" {
  name = "${var.project_name}-sla-alerts-${var.environment}"

  tags = {
    Name = "${var.project_name}-sla-alerts"
  }
}

# SNS Topic Subscription: Subscribes the campus administrator's email to receive instant breach notifications.
resource "aws_sns_topic_subscription" "admin_email" {
  topic_arn = aws_sns_topic.admin_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

