"""
Update Incident Status Lambda Handler.
AWS Resource: AWS Lambda Function (update_status).
Purpose: Allows assigned Maintenance Staff and Administrators to update ticket progress (e.g. IN_PROGRESS).
"""

import json
from typing import Dict, Any

try:
    from shared.db import get_table
    from shared.auth import get_user_info, is_in_group
    from shared.response import build_response
    from shared.utils import get_utc_iso
except ImportError:
    from ..shared.db import get_table
    from ..shared.auth import get_user_info, is_in_group
    from ..shared.response import build_response
    from ..shared.utils import get_utc_iso

ALLOWED_PROGRESS_STATUSES = ["IN_PROGRESS", "ASSIGNED", "OPEN"]


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for PATCH /incidents/{id}/status.
    Authorized for: Staff (assigned to ticket), Admin.
    """
    user = get_user_info(event)
    
    # 1. RBAC check
    if not is_in_group(user, ["Staff", "Admin"]):
        return build_response(403, {
            "error": "Forbidden: Only maintenance staff and administrators can update incident status."
        })

    # 2. Extract path parameter
    path_params = event.get("pathParameters") or {}
    incident_id = path_params.get("id")
    if not incident_id:
        return build_response(400, {"error": "Missing incident ID in request path."})

    # 3. Parse and validate JSON request body
    body_raw = event.get("body") or "{}"
    if isinstance(body_raw, str):
        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            return build_response(400, {"error": "Invalid JSON in request body."})
    elif isinstance(body_raw, dict):
        body = body_raw
    else:
        return build_response(400, {"error": "Malformed request body."})

    new_status = body.get("status")
    if not new_status or not isinstance(new_status, str):
        return build_response(400, {"error": "A valid 'status' string is required."})

    new_status = new_status.upper().strip()
    if new_status not in ALLOWED_PROGRESS_STATUSES:
        return build_response(400, {
            "error": (
                f"Invalid status transition. Allowed values: {', '.join(ALLOWED_PROGRESS_STATUSES)}. "
                "Use the resolve endpoint to close tickets."
            )
        })

    # 4. Fetch current incident record
    table = get_table()
    try:
        current_res = table.get_item(Key={"incident_id": incident_id})
    except Exception as e:
        return build_response(500, {"error": f"Database read failed: {str(e)}"})

    current_item = current_res.get("Item")
    if not current_item:
        return build_response(404, {"error": f"Incident with ID '{incident_id}' not found."})

    if current_item.get("status") in ["RESOLVED", "CLOSED"]:
        return build_response(400, {
            "error": f"Cannot modify status of an incident that is already {current_item.get('status')}."
        })

    # 5. Check Staff Assignment: Staff can only update their own assigned incidents
    is_admin = is_in_group(user, ["Admin"])
    if not is_admin:
        assigned_to = current_item.get("assigned_to")
        if assigned_to not in [user["user_id"], user["email"]]:
            return build_response(403, {
                "error": "Forbidden: You can only update incidents assigned to you."
            })

    # 6. Update DynamoDB item
    now_iso = get_utc_iso()
    notes = body.get("notes")

    update_expression = "SET #status = :s, #updated_at = :ua"
    expression_attr_names = {
        "#status": "status",
        "#updated_at": "updated_at"
    }
    expression_attr_values = {
        ":s": new_status,
        ":ua": now_iso
    }

    if notes and isinstance(notes, str) and notes.strip():
        update_expression += ", #notes = :n"
        expression_attr_names["#notes"] = "progress_notes"
        expression_attr_values[":n"] = notes.strip()

    try:
        update_res = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attr_names,
            ExpressionAttributeValues=expression_attr_values,
            ReturnValues="ALL_NEW"
        )
        updated_incident = update_res.get("Attributes")
    except Exception as e:
        return build_response(500, {"error": f"Failed to update incident: {str(e)}"})

    return build_response(200, {
        "message": f"Incident status updated to {new_status}.",
        "incident": updated_incident
    })

