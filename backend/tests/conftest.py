"""
Pytest Fixtures and Mock AWS Setup using Moto.
AWS Resource Mock: Amazon DynamoDB Local Emulation.
Purpose: Sets up in-memory mock DynamoDB table with identical schema and GSIs to test Lambdas without touching real AWS.
"""

import os
import sys
import json
import pytest
import boto3
from moto import mock_aws

# Ensure backend/src is on the Python path
BACKEND_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if BACKEND_SRC not in sys.path:
    sys.path.insert(0, BACKEND_SRC)

# Set mock AWS environment variables
os.environ["AWS_DEFAULT_REGION"] = "ap-south-1"
os.environ["AWS_REGION"] = "ap-south-1"
os.environ["AWS_ACCESS_KEY_ID"] = "mock_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "mock_secret"
os.environ["AWS_SECURITY_TOKEN"] = "mock_token"
os.environ["AWS_SESSION_TOKEN"] = "mock_session"
os.environ["INCIDENTS_TABLE_NAME"] = "campusops-incidents"


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-south-1"


@pytest.fixture(scope="function")
def dynamodb_table(aws_credentials):
    """
    Creates an in-memory DynamoDB table matching the production schema and GSIs:
    - Primary Key: incident_id (HASH)
    - CreatedByGSI: created_by (HASH), created_at (RANGE)
    - AssignedToGSI: assigned_to (HASH), created_at (RANGE)
    - StatusGSI: status (HASH), sla_deadline (RANGE)
    """
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
        
        table = dynamodb.create_table(
            TableName="campusops-incidents",
            KeySchema=[
                {"AttributeName": "incident_id", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "incident_id", "AttributeType": "S"},
                {"AttributeName": "created_by", "AttributeType": "S"},
                {"AttributeName": "assigned_to", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
                {"AttributeName": "sla_deadline", "AttributeType": "S"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "CreatedByGSI",
                    "KeySchema": [
                        {"AttributeName": "created_by", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                },
                {
                    "IndexName": "AssignedToGSI",
                    "KeySchema": [
                        {"AttributeName": "assigned_to", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                },
                {
                    "IndexName": "StatusGSI",
                    "KeySchema": [
                        {"AttributeName": "status", "KeyType": "HASH"},
                        {"AttributeName": "sla_deadline", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        yield table


def build_apigw_event(
    body=None,
    path_parameters=None,
    query_string_parameters=None,
    role="Student",
    user_id="user-sub-1234",
    email="student@college.edu"
):
    """
    Helper fixture to craft realistic API Gateway events with Cognito claims.
    """
    body_str = json.dumps(body) if isinstance(body, dict) else (body or "")
    
    return {
        "body": body_str,
        "pathParameters": path_parameters or {},
        "queryStringParameters": query_string_parameters or {},
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": user_id,
                    "email": email,
                    "cognito:username": email,
                    "cognito:groups": role if isinstance(role, str) else ",".join(role)
                }
            }
        }
    }

