# ==============================================================================
# Outputs for CampusOps Terraform Infrastructure
# Purpose: Exports key endpoints and IDs required for frontend .env configuration and testing.
# ==============================================================================

output "api_endpoint_url" {
  description = "Base URL of the deployed Amazon API Gateway REST API stage"
  value       = aws_api_gateway_stage.stage.invoke_url
}

output "cognito_user_pool_id" {
  description = "ID of the Amazon Cognito User Pool for user authentication"
  value       = aws_cognito_user_pool.pool.id
}

output "cognito_app_client_id" {
  description = "ID of the Amazon Cognito App Client used by the React web application"
  value       = aws_cognito_user_pool_client.client.id
}

output "s3_frontend_bucket_name" {
  description = "Name of the S3 bucket hosting the compiled React web application"
  value       = aws_s3_bucket.frontend.id
}

output "s3_website_endpoint" {
  description = "Direct HTTP URL of the S3 static website hosting bucket"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "frontend_url" {
  description = "Web URL of the static website hosting bucket"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "dynamodb_table_name" {
  description = "Name of the Amazon DynamoDB table storing incident tickets"
  value       = aws_dynamodb_table.incidents.name
}

output "sns_topic_arn" {
  description = "ARN of the Amazon SNS topic dispatching SLA escalation alerts"
  value       = aws_sns_topic.admin_alerts.arn
}

output "cloudwatch_dashboard_name" {
  description = "Name of the centralized Amazon CloudWatch operational dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}
