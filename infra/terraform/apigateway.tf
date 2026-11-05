# ==============================================================================
# Amazon API Gateway REST API with Cognito Authorizer & CORS Support
# AWS Resource: Amazon API Gateway REST API connecting frontend to backend Lambdas.
# ==============================================================================

# REST API: Central entry point that routes web client HTTP requests to appropriate backend Lambda functions.
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "CampusOps serverless REST API with Cognito authentication and CORS"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Cognito Authorizer: Validates incoming user JWT tokens against the Cognito User Pool before invoking Lambdas.
resource "aws_api_gateway_authorizer" "cognito" {
  name          = "${var.project_name}-cognito-auth"
  rest_api_id   = aws_api_gateway_rest_api.api.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [aws_cognito_user_pool.pool.arn]
}

# ------------------------------------------------------------------------------
# API Gateway Resources Hierarchy
# ------------------------------------------------------------------------------

# /incidents Resource: Base endpoint path for collection operations.
resource "aws_api_gateway_resource" "incidents" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "incidents"
}

# /incidents/{id} Resource: Endpoint path for operations on a specific incident ID.
resource "aws_api_gateway_resource" "incident_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.incidents.id
  path_part   = "{id}"
}

# /incidents/{id}/assign Resource: Endpoint path for assigning technicians to an incident.
resource "aws_api_gateway_resource" "assign" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.incident_id.id
  path_part   = "assign"
}

# /incidents/{id}/status Resource: Endpoint path for updating an incident's progress status.
resource "aws_api_gateway_resource" "status" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.incident_id.id
  path_part   = "status"
}

# /incidents/{id}/resolve Resource: Endpoint path for marking an incident resolved with notes.
resource "aws_api_gateway_resource" "resolve" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.incident_id.id
  path_part   = "resolve"
}

# ------------------------------------------------------------------------------
# HTTP Methods & Integrations
# ------------------------------------------------------------------------------

# POST /incidents -> create_incident Lambda
resource "aws_api_gateway_method" "post_incidents" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.incidents.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "post_incidents" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.incidents.id
  http_method             = aws_api_gateway_method.post_incidents.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_incident.invoke_arn
}

# GET /incidents -> list_incidents Lambda
resource "aws_api_gateway_method" "get_incidents" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.incidents.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "get_incidents" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.incidents.id
  http_method             = aws_api_gateway_method.get_incidents.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_incidents.invoke_arn
}

# GET /incidents/{id} -> get_incident Lambda
resource "aws_api_gateway_method" "get_incident_id" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.incident_id.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "get_incident_id" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.incident_id.id
  http_method             = aws_api_gateway_method.get_incident_id.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_incident.invoke_arn
}

# POST /incidents/{id}/assign -> assign_staff Lambda
resource "aws_api_gateway_method" "post_assign" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.assign.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "post_assign" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.assign.id
  http_method             = aws_api_gateway_method.post_assign.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.assign_staff.invoke_arn
}

# PATCH /incidents/{id}/status -> update_status Lambda
resource "aws_api_gateway_method" "patch_status" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.status.id
  http_method   = "PATCH"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "patch_status" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.status.id
  http_method             = aws_api_gateway_method.patch_status.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_status.invoke_arn
}

# POST /incidents/{id}/resolve -> resolve_incident Lambda
resource "aws_api_gateway_method" "post_resolve" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.resolve.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "post_resolve" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.resolve.id
  http_method             = aws_api_gateway_method.post_resolve.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.resolve_incident.invoke_arn
}

# ------------------------------------------------------------------------------
# CORS Preflight OPTIONS Handling for all 5 resources
# ------------------------------------------------------------------------------

locals {
  cors_resources = [
    aws_api_gateway_resource.incidents.id,
    aws_api_gateway_resource.incident_id.id,
    aws_api_gateway_resource.assign.id,
    aws_api_gateway_resource.status.id,
    aws_api_gateway_resource.resolve.id
  ]
}

# CORS OPTIONS Method: Enables browser preflight requests without requiring Cognito auth.
resource "aws_api_gateway_method" "options" {
  count         = length(local.cors_resources)
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = local.cors_resources[count.index]
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# CORS OPTIONS Mock Integration: Returns standard HTTP 200 immediately to browser preflight probes.
resource "aws_api_gateway_integration" "options" {
  count       = length(local.cors_resources)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = local.cors_resources[count.index]
  http_method = aws_api_gateway_method.options[count.index].http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# CORS OPTIONS Method Response: Declares permitted CORS headers.
resource "aws_api_gateway_method_response" "options" {
  count       = length(local.cors_resources)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = local.cors_resources[count.index]
  http_method = aws_api_gateway_method.options[count.index].http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

# CORS OPTIONS Integration Response: Populates permitted headers for browser preflight success.
resource "aws_api_gateway_integration_response" "options" {
  count       = length(local.cors_resources)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = local.cors_resources[count.index]
  http_method = aws_api_gateway_method.options[count.index].http_method
  status_code = aws_api_gateway_method_response.options[count.index].status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT,PATCH,DELETE'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [aws_api_gateway_integration.options]
}

# Gateway Response 4XX: Ensures 401/403 Cognito authentication rejection errors include CORS headers.
resource "aws_api_gateway_gateway_response" "response_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  response_type = "DEFAULT_4XX"

  response_templates = {
    "application/json" = "{\"message\":$context.error.messageString}"
  }

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT,PATCH,DELETE'"
  }
}

# Gateway Response 5XX: Ensures server error responses include CORS headers for browser debugging.
resource "aws_api_gateway_gateway_response" "response_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  response_type = "DEFAULT_5XX"

  response_templates = {
    "application/json" = "{\"message\":$context.error.messageString}"
  }

  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT,PATCH,DELETE'"
  }
}

# ------------------------------------------------------------------------------
# Lambda Invocation Permissions
# ------------------------------------------------------------------------------

locals {
  lambda_functions = {
    create  = aws_lambda_function.create_incident
    get     = aws_lambda_function.get_incident
    list    = aws_lambda_function.list_incidents
    assign  = aws_lambda_function.assign_staff
    status  = aws_lambda_function.update_status
    resolve = aws_lambda_function.resolve_incident
  }
}

# Lambda Permission: Grants API Gateway permission to trigger each backend Lambda function.
resource "aws_lambda_permission" "apigw_lambda" {
  for_each      = local.lambda_functions
  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# ------------------------------------------------------------------------------
# Deployment and Stage
# ------------------------------------------------------------------------------

# API Gateway Deployment: Packages API resources, methods, and integrations into an immutable release snapshot.
resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.incidents.id,
      aws_api_gateway_resource.incident_id.id,
      aws_api_gateway_resource.assign.id,
      aws_api_gateway_resource.status.id,
      aws_api_gateway_resource.resolve.id,
      aws_api_gateway_method.post_incidents.id,
      aws_api_gateway_method.get_incidents.id,
      aws_api_gateway_method.get_incident_id.id,
      aws_api_gateway_method.post_assign.id,
      aws_api_gateway_method.patch_status.id,
      aws_api_gateway_method.post_resolve.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.post_incidents,
    aws_api_gateway_integration.get_incidents,
    aws_api_gateway_integration.get_incident_id,
    aws_api_gateway_integration.post_assign,
    aws_api_gateway_integration.patch_status,
    aws_api_gateway_integration.post_resolve,
    aws_api_gateway_integration.options
  ]
}

# API Gateway Stage: Publishes the deployment under an accessible public stage name (e.g. dev).
resource "aws_api_gateway_stage" "stage" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = var.environment
}
