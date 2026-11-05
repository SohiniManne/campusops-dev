"""
Shared HTTP Response Formatter with CORS Support.
AWS Resource: API Gateway Integration Helper.
Purpose: Formats Python dictionaries into JSON responses compatible with API Gateway REST and HTTP APIs.
"""

import json
from decimal import Decimal
from typing import Any, Dict


class DecimalEncoder(json.JSONEncoder):
    """
    JSON encoder that converts DynamoDB Decimal objects to standard Python int or float.
    DynamoDB returns all numbers as Decimals, which the standard json.dumps cannot serialize.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def build_response(status_code: int, body: Any) -> Dict[str, Any]:
    """
    Generates an API Gateway proxy response with CORS headers and JSON payload.
    
    Args:
        status_code: HTTP status code (200, 201, 400, 403, 404, 500)
        body: Python dictionary or list representing response payload
        
    Returns:
        dict: API Gateway proxy response format
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PATCH,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }

