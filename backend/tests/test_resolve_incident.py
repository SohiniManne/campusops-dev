"""
Tests for resolve_incident Lambda.
AWS Resource: Lambda function under test with Moto DynamoDB.
"""

import json
from lambdas.resolve_incident import lambda_handler
from conftest import build_apigw_event


def insert_incident(table, incident_id="inc-res-1", status="IN_PROGRESS", assigned_to="staff-101"):
    item = {
        "incident_id": incident_id,
        "title": "Corridor Light Fixture Burnt",
        "category": "ELECTRICAL",
        "priority": "HIGH",
        "status": status,
        "created_by": "student-1",
        "assigned_to": assigned_to,
        "assigned_to_name": "Test Electrician",
        "created_at": "2026-11-05T01:00:00Z"
    }
    table.put_item(Item=item)
    return item


def test_assigned_staff_resolves_incident_success(dynamodb_table):
    """Assigned technician resolves incident providing descriptive resolution notes."""
    insert_incident(dynamodb_table, "inc-res-1", status="IN_PROGRESS", assigned_to="staff-101")

    payload = {
        "resolution_notes": "Replaced burnt 24W LED ballast and bulb. Tested circuit breaker; working normally."
    }
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-res-1"},
        role="Staff",
        user_id="staff-101",
        email="electrician@college.edu"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    updated = body["incident"]
    assert updated["status"] == "RESOLVED"
    assert updated["resolution_notes"] == payload["resolution_notes"]
    assert updated["resolved_by"] == "electrician@college.edu"
    assert updated["resolved_at"] is not None


def test_missing_or_short_resolution_notes(dynamodb_table):
    """Resolution notes are mandatory to ensure viva defense accountability."""
    insert_incident(dynamodb_table, "inc-res-2", status="IN_PROGRESS", assigned_to="staff-101")

    # Too short (< 5 chars)
    payload = {"resolution_notes": "Done"}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-res-2"},
        role="Staff",
        user_id="staff-101"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
    assert "at least 5 characters" in json.loads(res["body"])["error"]


def test_student_cannot_resolve_incident(dynamodb_table):
    """Students cannot resolve incidents."""
    insert_incident(dynamodb_table, "inc-res-3", status="IN_PROGRESS", assigned_to="staff-101")

    payload = {"resolution_notes": "Self resolved."}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-res-3"},
        role="Student",
        user_id="student-1"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 403


def test_unassigned_staff_cannot_resolve(dynamodb_table):
    """Staff not assigned to ticket cannot resolve it."""
    insert_incident(dynamodb_table, "inc-res-4", status="IN_PROGRESS", assigned_to="staff-101")

    payload = {"resolution_notes": "Attempted resolve."}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-res-4"},
        role="Staff",
        user_id="staff-999"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 403


def test_cannot_resolve_already_resolved_incident(dynamodb_table):
    """Cannot re-resolve an incident already marked as RESOLVED."""
    insert_incident(dynamodb_table, "inc-res-5", status="RESOLVED", assigned_to="staff-101")

    payload = {"resolution_notes": "Trying again."}
    event = build_apigw_event(
        body=payload,
        path_parameters={"id": "inc-res-5"},
        role="Staff",
        user_id="staff-101"
    )

    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
    assert "already RESOLVED" in json.loads(res["body"])["error"]

