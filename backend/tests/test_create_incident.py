"""
Tests for create_incident Lambda.
AWS Resource: Lambda function under test with Moto DynamoDB.
"""

import json
from datetime import datetime, timezone
from lambdas.create_incident import lambda_handler
from conftest import build_apigw_event
from shared.utils import parse_iso


def test_student_create_incident_success(dynamodb_table):
    """Verify Student can successfully create an incident with valid data."""
    payload = {
        "title": "Broken Lab Projector",
        "description": "The projector in Lab 204 will not turn on despite power switch being active.",
        "category": "LAB_EQUIPMENT",
        "priority": "HIGH",
        "location": "Academic Block A, Lab 204"
    }
    event = build_apigw_event(
        body=payload,
        role="Student",
        user_id="student-101",
        email="rahul@college.edu"
    )

    response = lambda_handler(event, None)
    assert response["statusCode"] == 201

    body = json.loads(response["body"])
    assert "incident" in body
    incident = body["incident"]

    assert incident["title"] == "Broken Lab Projector"
    assert incident["status"] == "OPEN"
    assert incident["priority"] == "HIGH"
    assert incident["category"] == "LAB_EQUIPMENT"
    assert incident["created_by"] == "student-101"
    assert incident["created_by_name"] == "rahul@college.edu"
    assert incident["sla_hours"] == 4
    assert incident["sla_status"] == "OK"
    assert incident["incident_id"].startswith("inc-")

    # Verify deadline is approximately 4 hours ahead of created_at
    created_at = parse_iso(incident["created_at"])
    sla_deadline = parse_iso(incident["sla_deadline"])
    diff_hours = (sla_deadline - created_at).total_seconds() / 3600
    assert round(diff_hours) == 4

    # Verify item is actually in DynamoDB
    db_item = dynamodb_table.get_item(Key={"incident_id": incident["incident_id"]})["Item"]
    assert db_item["title"] == "Broken Lab Projector"


def test_sla_deadline_by_priority(dynamodb_table):
    """Test SLA calculation across all 4 priority levels."""
    priority_tests = [
        ("CRITICAL", 1),
        ("HIGH", 4),
        ("MEDIUM", 12),
        ("LOW", 24)
    ]

    for priority, expected_hours in priority_tests:
        payload = {
            "title": f"Test {priority} Incident",
            "description": f"Testing SLA window for {priority} priority level.",
            "category": "ELECTRICAL",
            "priority": priority,
            "location": "Hostel 1, Room 12"
        }
        event = build_apigw_event(body=payload, role="Student")
        response = lambda_handler(event, None)
        assert response["statusCode"] == 201

        incident = json.loads(response["body"])["incident"]
        assert incident["sla_hours"] == expected_hours
        
        created_at = parse_iso(incident["created_at"])
        sla_deadline = parse_iso(incident["sla_deadline"])
        diff_hours = (sla_deadline - created_at).total_seconds() / 3600
        assert round(diff_hours) == expected_hours


def test_staff_cannot_create_incident(dynamodb_table):
    """Staff role is reserved for resolving/updating tickets, not reporting."""
    payload = {
        "title": "Test Maintenance Item",
        "description": "Staff trying to report.",
        "category": "PLUMBING",
        "priority": "LOW",
        "location": "Cafeteria"
    }
    event = build_apigw_event(body=payload, role="Staff")
    response = lambda_handler(event, None)
    assert response["statusCode"] == 403
    body = json.loads(response["body"])
    assert "Forbidden" in body["error"]


def test_unauthorized_user_cannot_create_incident(dynamodb_table):
    """Users without valid Cognito groups are denied."""
    payload = {
        "title": "Unauthorized Request",
        "description": "Testing missing group claims.",
        "category": "OTHER",
        "priority": "LOW",
        "location": "Library"
    }
    event = build_apigw_event(body=payload, role="")
    response = lambda_handler(event, None)
    assert response["statusCode"] == 403


def test_validation_missing_or_short_fields(dynamodb_table):
    """Verify input validation rules."""
    # Title too short
    bad_title = {
        "title": "AB",
        "description": "Valid description length.",
        "category": "ELECTRICAL",
        "priority": "LOW",
        "location": "Block C"
    }
    res = lambda_handler(build_apigw_event(body=bad_title, role="Student"), None)
    assert res["statusCode"] == 400
    assert "Title is required" in json.loads(res["body"])["error"]

    # Description too short
    bad_desc = {
        "title": "Valid Title",
        "description": "No",
        "category": "ELECTRICAL",
        "priority": "LOW",
        "location": "Block C"
    }
    res = lambda_handler(build_apigw_event(body=bad_desc, role="Student"), None)
    assert res["statusCode"] == 400
    assert "Description is required" in json.loads(res["body"])["error"]

    # Invalid category
    bad_cat = {
        "title": "Valid Title",
        "description": "Valid description length.",
        "category": "INVALID_CAT",
        "priority": "LOW",
        "location": "Block C"
    }
    res = lambda_handler(build_apigw_event(body=bad_cat, role="Student"), None)
    assert res["statusCode"] == 400
    assert "Category must be one of" in json.loads(res["body"])["error"]

    # Invalid priority
    bad_pri = {
        "title": "Valid Title",
        "description": "Valid description length.",
        "category": "PLUMBING",
        "priority": "SUPER_URGENT",
        "location": "Block C"
    }
    res = lambda_handler(build_apigw_event(body=bad_pri, role="Student"), None)
    assert res["statusCode"] == 400
    assert "Priority must be one of" in json.loads(res["body"])["error"]


def test_malformed_json_body(dynamodb_table):
    """Handling of invalid raw string JSON."""
    event = build_apigw_event(role="Student")
    event["body"] = "not a valid json {{"
    res = lambda_handler(event, None)
    assert res["statusCode"] == 400
    assert "Invalid JSON" in json.loads(res["body"])["error"]

