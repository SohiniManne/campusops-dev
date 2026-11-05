# ==============================================================================
# AWS IAM Roles and Least-Privilege Policies for Backend Lambdas
# AWS Resource: AWS IAM Execution Roles and Scoped Access Policies.
# ==============================================================================

# IAM Assume Role Policy Document: Grants AWS Lambda service permission to assume this execution role.
data "aws_iam_policy_document" "lambda_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# IAM Execution Role: Security role assumed by backend Lambdas during execution to interact with AWS services.
resource "aws_iam_role" "lambda_exec" {
  name               = "${var.project_name}-lambda-exec-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json

  tags = {
    Name = "${var.project_name}-lambda-exec-role"
  }
}

# IAM Policy Document: Grants strictly least-privilege permissions to DynamoDB table and CloudWatch logs.
data "aws_iam_policy_document" "lambda_permissions" {
  # CloudWatch Logging Permissions
  statement {
    sid    = "CloudWatchLogging"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*:*"]
  }

  # DynamoDB Least-Privilege Data Access
  statement {
    sid    = "DynamoDBTableAccess"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [
      aws_dynamodb_table.incidents.arn,
      "${aws_dynamodb_table.incidents.arn}/index/*"
    ]
  }

  # SNS Topic Publish Permission for SLA escalation notifications
  statement {
    sid       = "SNSPublishAlerts"
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.admin_alerts.arn]
  }
}

# IAM Role Policy Attachment: Attaches the least-privilege security policy directly to the Lambda execution role.
resource "aws_iam_role_policy" "lambda_policy_attachment" {
  name   = "${var.project_name}-lambda-least-privilege-${var.environment}"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}
