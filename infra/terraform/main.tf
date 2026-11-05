# ==============================================================================
# Main Terraform Configuration for CampusOps
# Region: ap-south-1 (Mumbai)
# Free Tier Optimized: Minimal resources, On-Demand billing, no idle cost
# ==============================================================================

terraform {
  required_version = "1.10.5"

  backend "s3" {
    bucket       = "campusops-terraform-state-418059030221"
    key          = "campusops/dev/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    # AWS Provider: Manages cloud resources in Amazon Web Services
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # Archive Provider: Generates zip archives of Lambda source code
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    # Random Provider: Generates unique suffixes for globally unique S3 bucket names
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Provider configuration with default tagging
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CampusOps"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Random suffix for uniquely naming S3 buckets
resource "random_id" "bucket_suffix" {
  byte_length = 4
}
