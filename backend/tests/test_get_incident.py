"""
Tests for get_incident Lambda.
AWS Resource: Lambda function under test with Moto DynamoDB.
"""

import json
from lambdas.get_incident import lambda_handler
from conftest import build_apigw_event


def insert_sample_incident(table, incident_id="inc-100", created_by="student-1", assigned_to=None):
    """Helper to insert an incident record directly into DynamoDB."""
    item = {
        "incident_id": incident_id,
        "title": "Air Conditioner Leaking",
        "description": "Water leaking steadily from indoor unit.",
        "category": "PLUMBING",
        "priority": "MEDIUM",
        "location": "Seminar Hall 1",
        "status": "OPEN",
        "created_by": created_by,
        "created_by_name": f"{created_by}@college.edu",
        "created_at": "2026-11-05T08:00:00Z",
        "sla_hours": 12,
        "sla_deadline": "2026-11-05T20:00:00Z",
        "sla_status": "OK",
        "updated_at": "2026-11-05T08:00:00Z"
    }
    if assigned_to:
        item["assigned_to"] = assigned_to
        item["assigned_to_name"] = f"{assigned_to}@college.edu"
    table.put_item(Item=item)
    return item


def test_student_can_get_own_incident(dynamodb_table):
    """Student can view their own reported incident."""
    insert_sample_incident(dynamodb_table, incident_id="inc-101", created_by="student-alice")

    event = build_apigw_event(
        path_parameters={"id": "inc-101"},
        role="Student",
        user_id="student-alice"
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert body["incident"]["incident_id"] == "inc-101"
    assert body["incident"]["title"] == "Air Conditioner Leaking"


def test_student_cannot_get_other_student_incident(dynamodb_table):
    """Student is forbidden from viewing incidents reported by another student."""
    insert_sample_incident(dynamodb_table, incident_id="inc-102", created_by="student-bob")

    event = build_apigw_event(
        path_parameters={"id": "inc-102"},
        role="Student",
        user_id="student-eve"
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 403
    assert "Forbidden" in json.loads(res["body"])["error"]


def test_staff_and_admin_can_view_any_incident(dynamodb_table):
    """Staff and Admin can inspect any incident for maintenance and triage."""
    insert_sample_incident(dynamodb_table, incident_id="inc-103", created_by="student-bob")

    # Staff test
    staff_event = build_apigw_event(
        path_parameters={"id": "inc-103"},
        role="Staff",
        user_id="staff-tech-1"
    )
    res_staff = lambda_handler(staff_event, None)
    assert res_staff["statusCode"] == 200

    # Admin test
    admin_event = build_apigw_event(
        path_parameters={"id": "inc-103"},
        role="Admin",
        user_id="admin-super"
    )
    res_admin = lambda_handler(admin_event, None)
    assert res_admin["statusCode"] == 200


def test_get_nonexistent_incident(dynamodb_table):
    """Returns 404 if incident does not exist."""
    event = build_apigw_event(
        path_parameters={"id": "inc-nonexistent"},
        role="Admin"
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 404
    assert "not found" in json.loads(res["body"])["error"]


def test_get_missing_path_parameter(dynamodb_table):
    """Returns 400 if ID is missing from path."""
    event = build_apigw_event(path_parameters={}, role="Admin")
    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
