"""
Tests for list_incidents Lambda.
AWS Resource: Lambda function under test with Moto DynamoDB GSIs.
"""

import json
from lambdas.list_incidents import lambda_handler
from conftest import build_apigw_event


def seed_test_incidents(table):
    """Seeds DynamoDB with multiple incidents across different students, staff, and statuses."""
    items = [
        {
            "incident_id": "inc-1",
            "title": "Wi-Fi Down in Hostel 3",
            "category": "WIFI_NETWORK",
            "priority": "CRITICAL",
            "status": "OPEN",
            "created_by": "student-alice",
            "created_at": "2026-11-05T01:00:00Z",
            "assigned_to": "staff-network",
            "sla_deadline": "2026-11-05T02:00:00Z"
        },
        {
            "incident_id": "inc-2",
            "title": "Broken Desk in Classroom 101",
            "category": "CLASSROOM_INFRA",
            "priority": "LOW",
            "status": "IN_PROGRESS",
            "created_by": "student-alice",
            "created_at": "2026-11-05T02:00:00Z",
            "assigned_to": "staff-carpenter",
            "sla_deadline": "2026-11-06T02:00:00Z"
        },
        {
            "incident_id": "inc-3",
            "title": "Flickering Light in Lab 1",
            "category": "ELECTRICAL",
            "priority": "MEDIUM",
            "status": "OPEN",
            "created_by": "student-bob",
            "created_at": "2026-11-05T03:00:00Z",
            "assigned_to": "staff-network",
            "sla_deadline": "2026-11-05T15:00:00Z"
        },
        {
            "incident_id": "inc-4",
            "title": "Water Tap Broken",
            "category": "PLUMBING",
            "priority": "HIGH",
            "status": "RESOLVED",
            "created_by": "student-bob",
            "created_at": "2026-11-05T04:00:00Z",
            "assigned_to": "staff-plumber",
            "sla_deadline": "2026-11-05T08:00:00Z"
        }
    ]
    for item in items:
        table.put_item(Item=item)


def test_student_lists_only_own_incidents(dynamodb_table):
    """Alice should only see inc-1 and inc-2, never Bob's incidents."""
    seed_test_incidents(dynamodb_table)

    event = build_apigw_event(role="Student", user_id="student-alice")
    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    incidents = body["incidents"]
    assert len(incidents) == 2
    ids = {i["incident_id"] for i in incidents}
    assert ids == {"inc-1", "inc-2"}


def test_staff_lists_only_assigned_incidents(dynamodb_table):
    """staff-network should see inc-1 and inc-3."""
    seed_test_incidents(dynamodb_table)

    event = build_apigw_event(role="Staff", user_id="staff-network")
    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    incidents = body["incidents"]
    assert len(incidents) == 2
    ids = {i["incident_id"] for i in incidents}
    assert ids == {"inc-1", "inc-3"}


def test_admin_lists_all_incidents(dynamodb_table):
    """Admin sees all 4 incidents."""
    seed_test_incidents(dynamodb_table)

    event = build_apigw_event(role="Admin", user_id="admin-super")
    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    assert body["count"] == 4


def test_admin_filters_by_status(dynamodb_table):
    """Admin filtering by status=OPEN should get inc-1 and inc-3."""
    seed_test_incidents(dynamodb_table)

    event = build_apigw_event(
        role="Admin",
        user_id="admin-super",
        query_string_parameters={"status": "OPEN"}
    )
    res = lambda_handler(event, None)
    assert res["statusCode"] == 200

    body = json.loads(res["body"])
    incidents = body["incidents"]
    assert len(incidents) == 2
    for inc in incidents:
        assert inc["status"] == "OPEN"

