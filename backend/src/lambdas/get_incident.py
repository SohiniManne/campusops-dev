"""
Get Incident Lambda Handler.
AWS Resource: AWS Lambda Function (get_incident).
Purpose: Retrieves single incident details from DynamoDB by ID and ensures role-based access restrictions.
"""

from typing import Dict, Any

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
    Entry point for GET /incidents/{id}.
    Authorized for: Student (own tickets), Staff (all), Admin (all).
    """
    # 1. Authenticate & extract user
    user = get_user_info(event)
    if not is_in_group(user, ["Student", "Staff", "Admin"]):
        return build_response(403, {"error": "Forbidden: Unrecognized or unauthorized user role."})

    # 2. Extract path parameter
    path_params = event.get("pathParameters") or {}
    incident_id = path_params.get("id")
    if not incident_id:
        return build_response(400, {"error": "Missing incident ID in request path."})

    # 3. Retrieve incident from DynamoDB
    table = get_table()
    try:
        response = table.get_item(Key={"incident_id": incident_id})
    except Exception as e:
        return build_response(500, {"error": f"Database query failed: {str(e)}"})

    item = response.get("Item")
    if not item:
        return build_response(404, {"error": f"Incident with ID '{incident_id}' not found."})

    # 4. RBAC Check: Students can only view their own reported tickets
    is_admin = is_in_group(user, ["Admin"])
    is_staff = is_in_group(user, ["Staff"])
    if not (is_admin or is_staff):
        if item.get("created_by") != user["user_id"]:
            return build_response(403, {
                "error": "Forbidden: You are only authorized to view incidents you reported."
            })

    return build_response(200, {"incident": item})

