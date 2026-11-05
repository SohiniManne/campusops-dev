"""
Tests for update_status Lambda.
AWS Resource: Lambda function under test with Moto DynamoDB.
"""

import json
from lambdas.update_status import lambda_handler
from conftest import build_apigw_event


def insert_incident(table, incident_id="inc-status-1", status="ASSIGNED", assigned_to="staff-101"):
    item = {
        "incident_id": incident_id,
        "title": "Lab Exhaust Fan Not Working",
        "category": "LAB_EQUIPMENT",
        "priority": "MEDIUM",
        "status": status,
        "created_by": "student-1",
        "assigned_to": assigned_to,
        "assigned_to_name": "Test Technician",
        "created_at": "2026-11-05T01:00:00Z"
    }
    table.put_item(Item=item)
    return item


def test_assigned_staff_updates_status_success(dynamodb_table):
    """Assigned technician can move status from ASSIGNED to IN_PROGRESS."""
    insert_incident(dynamodb_table, "inc-status-1", status="ASSIGNED", assigned_to="staff-101")

    payload = {
        "status": "IN_PROGRESS",
        "notes": "Arrived at Lab, motor inspected, replacing capacitor."
    }
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-status-1"},
        role="Staff",
        user_id="staff-101"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    updated = body["incident"]
    assert updated["status"] == "IN_PROGRESS"
    assert updated["progress_notes"] == "Arrived at Lab, motor inspected, replacing capacitor."


def test_unassigned_staff_cannot_update_status(dynamodb_table):
    """A staff member not assigned to this incident is rejected with 403."""
    insert_incident(dynamodb_table, "inc-status-2", status="ASSIGNED", assigned_to="staff-101")

    payload = {"status": "IN_PROGRESS"}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-status-2"},
        role="Staff",
        user_id="staff-999"  # Different staff member
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 403
    assert "Forbidden" in json.loads(res["body"])["error"]


def test_student_cannot_update_status(dynamodb_table):
    """Students cannot update status."""
    insert_incident(dynamodb_table, "inc-status-3", status="ASSIGNED", assigned_to="staff-101")

    payload = {"status": "IN_PROGRESS"}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-status-3"},
        role="Student",
        user_id="student-1"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 403


def test_invalid_status_value(dynamodb_table):
    """Passing an unrecognized status value yields 400 Bad Request."""
    insert_incident(dynamodb_table, "inc-status-4", status="ASSIGNED", assigned_to="staff-101")

    payload = {"status": "RANDOM_STATUS"}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-status-4"},
        role="Staff",
        user_id="staff-101"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
    assert "Invalid status transition" in json.loads(res["body"])["error"]

