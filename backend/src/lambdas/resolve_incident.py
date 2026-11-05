"""
Resolve Incident Lambda Handler.
AWS Resource: AWS Lambda Function (resolve_incident).
Purpose: Allows assigned Maintenance Staff or Administrators to mark a ticket as RESOLVED with mandatory resolution notes.
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
    Entry point for POST /incidents/{id}/resolve.
    Authorized for: Staff (assigned to ticket), Admin.
    """
    user = get_user_info(event)
    
    # 1. RBAC check
    if not is_in_group(user, ["Staff", "Admin"]):
        return build_response(403, {
            "error": "Forbidden: Only maintenance staff and administrators can resolve incidents."
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

    resolution_notes = body.get("resolution_notes")
    if not resolution_notes or not isinstance(resolution_notes, str) or len(resolution_notes.strip()) < 5:
        return build_response(400, {
            "error": "Resolution notes are required and must be at least 5 characters explaining what work was done."
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
            "error": f"Incident is already {current_item.get('status')}."
        })

    # 5. Check Staff Assignment: Staff can only resolve incidents assigned to them
    is_admin = is_in_group(user, ["Admin"])
    if not is_admin:
        assigned_to = current_item.get("assigned_to")
        if assigned_to not in [user["user_id"], user["email"]]:
            return build_response(403, {
                "error": "Forbidden: You can only resolve incidents assigned to you."
            })

    # 6. Update DynamoDB item to RESOLVED
    now_iso = get_utc_iso()

    try:
        update_res = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression="SET #status = :s, #notes = :n, #resolved_at = :ra, #resolved_by = :rb, #updated_at = :ua",
            ExpressionAttributeNames={
                "#status": "status",
                "#notes": "resolution_notes",
                "#resolved_at": "resolved_at",
                "#resolved_by": "resolved_by",
                "#updated_at": "updated_at"
            },
            ExpressionAttributeValues={
                ":s": "RESOLVED",
                ":n": resolution_notes.strip(),
                ":ra": now_iso,
                ":rb": user["email"],
                ":ua": now_iso
            },
            ReturnValues="ALL_NEW"
        )
        updated_incident = update_res.get("Attributes")
    except Exception as e:
        return build_response(500, {"error": f"Failed to update incident: {str(e)}"})

    return build_response(200, {
        "message": "Incident marked as RESOLVED successfully.",
        "incident": updated_incident
    })

