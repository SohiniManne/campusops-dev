# ==============================================================================
# Amazon Cognito User Authentication & Authorization Setup
# AWS Resource: Amazon Cognito User Pool, App Client, and Role-Based User Groups.
# ==============================================================================

# Cognito User Pool: Manages campus user identity, registration, sign-in, and password lifecycle.
resource "aws_cognito_user_pool" "pool" {
  name                     = "${var.project_name}-users-${var.environment}"
  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Name = "${var.project_name}-user-pool"
  }
}

# Cognito User Pool Client: Enables the React frontend web app to authenticate users and acquire JWT tokens.
resource "aws_cognito_user_pool_client" "client" {
  name         = "${var.project_name}-web-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.pool.id

  generate_secret               = false # Public client (browser React app cannot secure a client secret)
  prevent_user_existence_errors = "ENABLED"
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
  supported_identity_providers = ["COGNITO"]
}

# Cognito User Group (Student): Role group granting permission to submit maintenance tickets and view personal history.
resource "aws_cognito_user_group" "student_group" {
  name         = "Student"
  user_pool_id = aws_cognito_user_pool.pool.id
  description  = "Students who can report issues and monitor personal incident status."
  precedence   = 30
}

# Cognito User Group (Staff): Role group granting technicians permission to inspect assigned tasks and resolve issues.
resource "aws_cognito_user_group" "staff_group" {
  name         = "Staff"
  user_pool_id = aws_cognito_user_pool.pool.id
  description  = "Maintenance technicians who update ticket progress and submit resolution notes."
  precedence   = 20
}

# Cognito User Group (Admin): Role group granting full administrative access to assign staff, track SLAs, and view metrics.
resource "aws_cognito_user_group" "admin_group" {
  name         = "Admin"
  user_pool_id = aws_cognito_user_pool.pool.id
  description  = "Campus administrators with full management and assignment privileges."
  precedence   = 10
}
