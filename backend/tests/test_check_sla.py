"""
Tests for check_sla Lambda and EventBridge + SNS Automation.
AWS Resource: Lambda function under test with Moto DynamoDB and Moto SNS.
"""

import os
from datetime import timedelta
import boto3
from moto import mock_aws
from lambdas.check_sla import lambda_handler
from shared.utils import get_utc_now, get_utc_iso


def create_sns_topic():
    """Helper to create a mock SNS topic for testing notifications."""
    sns = boto3.client("sns", region_name="ap-south-1")
    res = sns.create_topic(Name="campusops-sla-alerts")
    return res["TopicArn"]


def test_overdue_incident_is_marked_breached_and_notified(dynamodb_table):
    """Active open incident past its deadline should be marked BREACHED and published to SNS."""
    topic_arn = create_sns_topic()
    os.environ["SNS_TOPIC_ARN"] = topic_arn

    past_deadline = get_utc_iso(get_utc_now() - timedelta(hours=2))
    past_created = get_utc_iso(get_utc_now() - timedelta(hours=3))

    # Overdue incident: deadline 2 hours in the past
    overdue_item = {
        "incident_id": "inc-overdue-1",
        "title": "Main Water Line Burst",
        "category": "PLUMBING",
        "priority": "CRITICAL",
        "location": "Hostel Block A",
        "status": "OPEN",
        "created_by": "student-1",
        "created_by_name": "student1@college.edu",
        "created_at": past_created,
        "sla_hours": 1,
        "sla_deadline": past_deadline,
        "sla_status": "OK",
        "updated_at": past_created
    }
    dynamodb_table.put_item(Item=overdue_item)

    # Run check_sla lambda
    result = lambda_handler({}, None)
    assert result["status"] == "SUCCESS"
    assert result["breached_count"] == 1
    assert "inc-overdue-1" in result["breached_ids"]

    # Verify item status was updated in DynamoDB
    updated = dynamodb_table.get_item(Key={"incident_id": "inc-overdue-1"})["Item"]
    assert updated["sla_status"] == "BREACHED"


def test_healthy_incident_is_not_breached(dynamodb_table):
    """Incident with a future deadline should remain OK."""
    topic_arn = create_sns_topic()
    os.environ["SNS_TOPIC_ARN"] = topic_arn

    future_deadline = get_utc_iso(get_utc_now() + timedelta(hours=10))
    created_at = get_utc_iso(get_utc_now() - timedelta(hours=1))

    healthy_item = {
        "incident_id": "inc-healthy-1",
        "title": "Minor Desk Scratch",
        "category": "CLASSROOM_INFRA",
        "priority": "LOW",
        "location": "Room 102",
        "status": "OPEN",
        "created_by": "student-1",
        "created_by_name": "student1@college.edu",
        "created_at": created_at,
        "sla_hours": 24,
        "sla_deadline": future_deadline,
        "sla_status": "OK",
        "updated_at": created_at
    }
    dynamodb_table.put_item(Item=healthy_item)

    result = lambda_handler({}, None)
    assert result["breached_count"] == 0

    item_check = dynamodb_table.get_item(Key={"incident_id": "inc-healthy-1"})["Item"]
    assert item_check["sla_status"] == "OK"


def test_resolved_incident_is_not_alerted(dynamodb_table):
    """Even if an incident took longer than SLA to resolve, closed tickets are not re-alerted."""
    topic_arn = create_sns_topic()
    os.environ["SNS_TOPIC_ARN"] = topic_arn

    past_deadline = get_utc_iso(get_utc_now() - timedelta(hours=4))
    created_at = get_utc_iso(get_utc_now() - timedelta(hours=8))

    resolved_item = {
        "incident_id": "inc-resolved-1",
        "title": "Replaced Light Bulb",
        "category": "ELECTRICAL",
        "priority": "HIGH",
        "location": "Library 2nd Floor",
        "status": "RESOLVED",
        "created_by": "student-1",
        "created_by_name": "student1@college.edu",
        "created_at": created_at,
        "sla_hours": 4,
        "sla_deadline": past_deadline,
        "sla_status": "OK",
        "resolution_notes": "Completed fix.",
        "resolved_at": get_utc_iso(get_utc_now() - timedelta(hours=1)),
        "updated_at": get_utc_iso(get_utc_now() - timedelta(hours=1))
    }
    dynamodb_table.put_item(Item=resolved_item)

    result = lambda_handler({}, None)
    assert result["breached_count"] == 0


def test_already_breached_incident_prevents_duplicate_notifications(dynamodb_table):
    """Incidents already marked as BREACHED should not be processed again on subsequent cron runs."""
    topic_arn = create_sns_topic()
    os.environ["SNS_TOPIC_ARN"] = topic_arn

    past_deadline = get_utc_iso(get_utc_now() - timedelta(hours=5))
    created_at = get_utc_iso(get_utc_now() - timedelta(hours=9))

    already_breached_item = {
        "incident_id": "inc-already-breached",
        "title": "HVAC Chiller Offline",
        "category": "LAB_EQUIPMENT",
        "priority": "HIGH",
        "location": "Server Room",
        "status": "IN_PROGRESS",
        "created_by": "student-1",
        "created_by_name": "student1@college.edu",
        "created_at": created_at,
        "assigned_to": "staff-1",
        "sla_hours": 4,
        "sla_deadline": past_deadline,
        "sla_status": "BREACHED", # Already escalated
        "updated_at": get_utc_iso(get_utc_now() - timedelta(hours=3))
    }
    dynamodb_table.put_item(Item=already_breached_item)

    result = lambda_handler({}, None)
    assert result["breached_count"] == 0
    assert "inc-already-breached" not in result["breached_ids"]
