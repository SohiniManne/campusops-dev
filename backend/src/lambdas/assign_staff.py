"""
Assign Staff Lambda Handler.
AWS Resource: AWS Lambda Function (assign_staff).
Purpose: Allows Administrators to assign maintenance staff to an open incident and update status to ASSIGNED.
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


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for POST /incidents/{id}/assign.
    Authorized for: Admin only.
    """
    user = get_user_info(event)
    
    # 1. RBAC check: Only Admin can assign staff members
    if not is_in_group(user, ["Admin"]):
        return build_response(403, {
            "error": "Forbidden: Only administrators can assign maintenance staff to incidents."
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

    assigned_to = body.get("assigned_to")
    assigned_to_name = body.get("assigned_to_name")

    if not assigned_to or not isinstance(assigned_to, str) or not assigned_to.strip():
        return build_response(400, {"error": "'assigned_to' (staff ID/email) is required."})

    if not assigned_to_name or not isinstance(assigned_to_name, str) or not assigned_to_name.strip():
        return build_response(400, {"error": "'assigned_to_name' (staff display name) is required."})

    # 4. Check if incident exists
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
            "error": f"Cannot assign an incident that is already {current_item.get('status')}."
        })

    # 5. Update DynamoDB with assigned staff details
    now_iso = get_utc_iso()
    new_status = "ASSIGNED" if current_item.get("status") == "OPEN" else current_item.get("status")

    try:
        update_res = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression=(
                "SET #assigned_to = :at, #assigned_to_name = :atn, "
                "#assigned_at = :aa, #status = :s, #updated_at = :ua"
            ),
            ExpressionAttributeNames={
                "#assigned_to": "assigned_to",
                "#assigned_to_name": "assigned_to_name",
                "#assigned_at": "assigned_at",
                "#status": "status",
                "#updated_at": "updated_at"
            },
            ExpressionAttributeValues={
                ":at": assigned_to.strip(),
                ":atn": assigned_to_name.strip(),
                ":aa": now_iso,
                ":s": new_status,
                ":ua": now_iso
            },
            ReturnValues="ALL_NEW"
        )
        updated_incident = update_res.get("Attributes")
    except Exception as e:
        return build_response(500, {"error": f"Failed to update incident: {str(e)}"})

    return build_response(200, {
        "message": f"Incident successfully assigned to {assigned_to_name.strip()}.",
        "incident": updated_incident
    })

