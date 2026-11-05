"""
List Incidents Lambda Handler.
AWS Resource: AWS Lambda Function (list_incidents).
Purpose: Lists incidents using DynamoDB Global Secondary Indexes (GSIs), scoped strictly to caller's role.
"""

from typing import Dict, Any, List
from boto3.dynamodb.conditions import Key

try:
    from shared.db import get_table
    from shared.auth import get_user_info, is_in_group
    from shared.response import build_response
except ImportError:
    from ..shared.db import get_table
    from ..shared.auth import get_user_info, is_in_group
    from ..shared.response import build_response


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for GET /incidents.
    Authorized for:
      - Student: Lists only tickets created by this student (via CreatedByGSI)
      - Staff: Lists tickets assigned to this staff member (via AssignedToGSI)
      - Admin: Lists all tickets or filters by status (via StatusGSI or Scan)
    """
    user = get_user_info(event)
    if not is_in_group(user, ["Student", "Staff", "Admin"]):
        return build_response(403, {"error": "Forbidden: Unrecognized or unauthorized user role."})

    query_params = event.get("queryStringParameters") or {}
    status_filter = query_params.get("status")
    if status_filter:
        status_filter = status_filter.upper()

    table = get_table()
    items: List[Dict[str, Any]] = []

    try:
        is_admin = is_in_group(user, ["Admin"])
        is_staff = is_in_group(user, ["Staff"])

        if is_admin:
            # Administrators can view all tickets, optionally filtered by status
            if status_filter:
                response = table.query(
                    IndexName="StatusGSI",
                    KeyConditionExpression=Key("status").eq(status_filter),
                    ScanIndexForward=False
                )
                items = response.get("Items", [])
            else:
                response = table.scan()
                items = response.get("Items", [])
        elif is_staff:
            # Staff can view incidents assigned to their user ID or email
            staff_id = user["user_id"]
            response = table.query(
                IndexName="AssignedToGSI",
                KeyConditionExpression=Key("assigned_to").eq(staff_id),
                ScanIndexForward=False
            )
            items = response.get("Items", [])
            # Also check if assigned by email if no items found and email differs
            if not items and user.get("email") and user["email"] != staff_id:
                resp_email = table.query(
                    IndexName="AssignedToGSI",
                    KeyConditionExpression=Key("assigned_to").eq(user["email"]),
                    ScanIndexForward=False
                )
                items = resp_email.get("Items", [])
        else:
            # Students can strictly only view incidents they reported
            student_id = user["user_id"]
            response = table.query(
                IndexName="CreatedByGSI",
                KeyConditionExpression=Key("created_by").eq(student_id),
                ScanIndexForward=False
            )
            items = response.get("Items", [])

        # Sort incidents newest first
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return build_response(200, {
            "incidents": items,
            "count": len(items)
        })

    except Exception as e:
        return build_response(500, {"error": f"Failed to retrieve incidents: {str(e)}"})

