# ==============================================================================
# Input Variables for CampusOps Terraform Infrastructure
# ==============================================================================

variable "aws_region" {
  description = "AWS deployment region (ap-south-1 Mumbai for college spec)"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project identifier prefix used across all resources"
  type        = string
  default     = "campusops"
}

variable "alert_email" {
  description = "Email address for administrative alerts and cost notifications"
  type        = string
  default     = "umeshreddy3005@gmail.com"
}

variable "budget_limit_usd" {
  description = "Monthly cost budget threshold in USD to guarantee AWS Free Tier safety"
  type        = string
  default     = "1.0"
}

