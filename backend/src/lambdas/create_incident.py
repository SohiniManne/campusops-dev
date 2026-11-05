"""
Create Incident Lambda Handler.
AWS Resource: AWS Lambda Function (create_incident).
Purpose: Validates user input, calculates SLA deadline based on priority, and saves the new incident to DynamoDB.
"""

import json
from typing import Dict, Any

try:
    from shared.db import get_table
    from shared.auth import get_user_info, is_in_group
    from shared.response import build_response
    from shared.utils import (
        calculate_sla_deadline,
        generate_incident_id,
        get_utc_iso,
        validate_incident_input
    )
except ImportError:
    from ..shared.db import get_table
    from ..shared.auth import get_user_info, is_in_group
    from ..shared.response import build_response
    from ..shared.utils import (
        calculate_sla_deadline,
        generate_incident_id,
        get_utc_iso,
        validate_incident_input
    )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for POST /incidents.
    Authorized for: Student, Admin.
    """
    # 1. Authenticate & extract caller details
    user = get_user_info(event)
    
    # 2. RBAC check: Student and Admin can report new incidents
    if not is_in_group(user, ["Student", "Admin"]):
        return build_response(403, {
            "error": "Forbidden: Only Students and Administrators can create incidents."
        })

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

    is_valid, error_msg = validate_incident_input(body)
    if not is_valid:
        return build_response(400, {"error": error_msg})

    # 4. Generate metadata and calculate SLA resolution target
    now_iso = get_utc_iso()
    priority = body["priority"].upper()
    sla_hours, sla_deadline = calculate_sla_deadline(priority)
    incident_id = generate_incident_id()

    # 5. Build DynamoDB incident record (sparse index: omit null GSI keys like assigned_to)
    incident = {
        "incident_id": incident_id,
        "title": body["title"].strip(),
        "description": body["description"].strip(),
        "category": body["category"].upper(),
        "priority": priority,
        "location": body["location"].strip(),
        "status": "OPEN",
        "created_by": user["user_id"],
        "created_by_name": user["email"],
        "created_at": now_iso,
        "sla_hours": sla_hours,
        "sla_deadline": sla_deadline,
        "sla_status": "OK",
        "updated_at": now_iso
    }

    # 6. Save item to DynamoDB
    table = get_table()
    try:
        table.put_item(Item=incident)
    except Exception as e:
        return build_response(500, {"error": f"Failed to save incident: {str(e)}"})

    return build_response(201, {
        "message": "Incident created successfully.",
        "incident": incident
    })
