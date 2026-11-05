"""
Tests for assign_staff Lambda.
AWS Resource: Lambda function under test with Moto DynamoDB.
"""

import json
from lambdas.assign_staff import lambda_handler
from conftest import build_apigw_event


def insert_incident(table, incident_id="inc-assign-1", status="OPEN"):
    item = {
        "incident_id": incident_id,
        "title": "Broken Window Latch",
        "category": "CLASSROOM_INFRA",
        "priority": "LOW",
        "status": status,
        "created_by": "student-1",
        "created_at": "2026-11-05T01:00:00Z"
    }
    table.put_item(Item=item)
    return item


def test_admin_assigns_staff_success(dynamodb_table):
    """Admin successfully assigns staff member to an open incident."""
    insert_incident(dynamodb_table, "inc-assign-1", status="OPEN")

    payload = {
        "assigned_to": "staff-user-456",
        "assigned_to_name": "Ramesh Kumar (Electrician)"
    }
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-assign-1"},
        role="Admin",
        user_id="admin-1"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    updated = body["incident"]
    assert updated["status"] == "ASSIGNED"
    assert updated["assigned_to"] == "staff-user-456"
    assert updated["assigned_to_name"] == "Ramesh Kumar (Electrician)"
    assert updated["assigned_at"] is not None


def test_student_cannot_assign_staff(dynamodb_table):
    """Students are forbidden from assigning tasks."""
    insert_incident(dynamodb_table, "inc-assign-2", status="OPEN")

    payload = {
        "assigned_to": "staff-user-456",
        "assigned_to_name": "Ramesh Kumar"
    }
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-assign-2"},
        role="Student"
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 403
    assert "Forbidden" in json.loads(res["body"])["error"]


def test_cannot_assign_resolved_incident(dynamodb_table):
    """Attempting to assign an already resolved ticket returns 400 Bad Request."""
    insert_incident(dynamodb_table, "inc-assign-3", status="RESOLVED")

    payload = {
        "assigned_to": "staff-user-456",
        "assigned_to_name": "Ramesh Kumar"
    }
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-assign-3"},
        role="Admin"
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
    assert "already RESOLVED" in json.loads(res["body"])["error"]


def test_assign_missing_fields(dynamodb_table):
    """Validation fails if assigned_to or assigned_to_name is absent."""
    insert_incident(dynamodb_table, "inc-assign-4", status="OPEN")

    # Missing assigned_to_name
    event = build_apigw_event(
        body={"assigned_to": "staff-user-456"},
        path_parameters={"id": "inc-assign-4"},
        role="Admin"
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
    assert "assigned_to_name" in json.loads(res["body"])["error"]

