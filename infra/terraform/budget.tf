# ==============================================================================
# AWS Budgets Zero-Cost / Low-Cost Safety Alert
# AWS Resource: AWS Budget Alert for Free Tier Cost Protection.
# ==============================================================================

# AWS Budget: Monitors monthly AWS cloud spending and sends automated email warnings to safeguard Free Tier.
resource "aws_budgets_budget" "cost_alert" {
  name              = "${var.project_name}-free-tier-budget-${var.environment}"
  budget_type       = "COST"
  limit_amount      = var.budget_limit_usd
  limit_unit        = "USD"
  time_period_start = "2026-01-01_00:00"
  time_unit         = "MONTHLY"

  # Warning Alert: Triggers when actual spend reaches 80% ($0.80)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }

  # Forecast Alert: Triggers immediately if AWS forecasts total monthly spend will exceed $1.00
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.alert_email]
  }
}

