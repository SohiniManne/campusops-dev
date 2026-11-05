# ==============================================================================
# Amazon DynamoDB Table Definition
# AWS Resource: Amazon DynamoDB NoSQL Database Table for incident storage.
# ==============================================================================

# DynamoDB Table: Stores all campus maintenance incident tickets with single-digit millisecond latency.
resource "aws_dynamodb_table" "incidents" {
  name         = "${var.project_name}-incidents-${var.environment}"
  billing_mode = "PAY_PER_REQUEST" # Free Tier: On-demand avoids hourly idle capacity fees
  hash_key     = "incident_id"

  attribute {
    name = "incident_id"
    type = "S"
  }

  attribute {
    name = "created_by"
    type = "S"
  }

  attribute {
    name = "assigned_to"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  attribute {
    name = "sla_deadline"
    type = "S"
  }

  # GSI 1: CreatedByGSI - Enables students to quickly list their own submitted tickets without full table scans.
  global_secondary_index {
    name            = "CreatedByGSI"
    hash_key        = "created_by"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  # GSI 2: AssignedToGSI - Enables maintenance technicians to query tasks assigned directly to them.
  global_secondary_index {
    name            = "AssignedToGSI"
    hash_key        = "assigned_to"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  # GSI 3: StatusGSI - Enables administrators and the SLA monitor cron to query active tickets sorted by SLA deadline.
  global_secondary_index {
    name            = "StatusGSI"
    hash_key        = "status"
    range_key       = "sla_deadline"
    projection_type = "ALL"
  }

  # Default AWS managed encryption at rest (100% Free)
  server_side_encryption {
    enabled = true
  }

  tags = {
    Name = "${var.project_name}-incidents"
  }
}

