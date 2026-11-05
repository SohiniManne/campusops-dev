# ==============================================================================
# AWS Lambda Functions Definition and Packaging
# AWS Resource: AWS Lambda Serverless Functions running Python 3.12 runtime.
# ==============================================================================

# Archive File Data Source: Bundles Python backend source code into a zip artifact for Lambda deployment.
data "archive_file" "backend_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/src"
  output_path = "${path.module}/build/backend.zip"
}

# 1. Create Incident Lambda: Validates payload, calculates SLA deadline, and saves record to DynamoDB.
resource "aws_lambda_function" "create_incident" {
  function_name    = "${var.project_name}-create-incident-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.create_incident.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }

  tags = {
    Name = "${var.project_name}-create-incident"
  }
}

# 2. Get Incident Lambda: Fetches details for a single ticket while enforcing student ownership privacy.
resource "aws_lambda_function" "get_incident" {
  function_name    = "${var.project_name}-get-incident-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.get_incident.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }

  tags = {
    Name = "${var.project_name}-get-incident"
  }
}

# 3. List Incidents Lambda: Queries DynamoDB GSIs according to the caller's role (Student, Staff, Admin).
resource "aws_lambda_function" "list_incidents" {
  function_name    = "${var.project_name}-list-incidents-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.list_incidents.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }

  tags = {
    Name = "${var.project_name}-list-incidents"
  }
}

# 4. Assign Staff Lambda: Enforces admin role to allocate maintenance technicians to open incidents.
resource "aws_lambda_function" "assign_staff" {
  function_name    = "${var.project_name}-assign-staff-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.assign_staff.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }

  tags = {
    Name = "${var.project_name}-assign-staff"
  }
}

# 5. Update Status Lambda: Enables technicians and admins to mark tickets IN_PROGRESS and log updates.
resource "aws_lambda_function" "update_status" {
  function_name    = "${var.project_name}-update-status-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.update_status.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }

  tags = {
    Name = "${var.project_name}-update-status"
  }
}

# 6. Resolve Incident Lambda: Closes tickets requiring mandatory notes and captures completion metadata.
resource "aws_lambda_function" "resolve_incident" {
  function_name    = "${var.project_name}-resolve-incident-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.resolve_incident.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }

  tags = {
    Name = "${var.project_name}-resolve-incident"
  }
}

# 7. Check SLA Lambda: Cron function triggered by EventBridge to detect overdue incidents and alert admins via SNS.
resource "aws_lambda_function" "check_sla" {
  function_name    = "${var.project_name}-check-sla-${var.environment}"
  filename         = data.archive_file.backend_zip.output_path
  source_code_hash = data.archive_file.backend_zip.output_base64sha256
  runtime          = "python3.12"
  handler          = "lambdas.check_sla.lambda_handler"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 30
  memory_size      = 128

  environment {
    variables = {
      INCIDENTS_TABLE_NAME = aws_dynamodb_table.incidents.name
      SNS_TOPIC_ARN        = aws_sns_topic.admin_alerts.arn
    }
  }

  tags = {
    Name = "${var.project_name}-check-sla"
  }
}

