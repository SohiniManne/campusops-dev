"""
Shared DynamoDB Connection and Query Helper.
AWS Resource: Amazon DynamoDB Table Resource.
Purpose: Connects to DynamoDB table using Boto3, supporting environment-based configuration and testing mocks.
"""

import os
import boto3
from typing import Any

# Table name configured via Lambda environment variable set by Terraform
TABLE_NAME = os.environ.get("INCIDENTS_TABLE_NAME", "campusops-incidents")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")


def get_dynamodb_resource() -> Any:
    """
    Returns Boto3 DynamoDB resource.
    Supports moto mocking in unit tests and AWS credentials in Lambda execution.
    """
    return boto3.resource("dynamodb", region_name=AWS_REGION)


def get_table() -> Any:
    """
    Returns the DynamoDB Table instance for CampusOps incidents.
    """
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(TABLE_NAME)

