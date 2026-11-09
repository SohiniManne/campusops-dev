"""
Check SLA Lambda Handler.
AWS Resource: AWS Lambda Function (check_sla).
Purpose: Periodically scans active incidents past their SLA resolution deadline,
marks them as BREACHED in DynamoDB, and dispatches automated SNS email alerts to administrators.
"""

import os
import json
import boto3
from typing import Dict, Any, List
from boto3.dynamodb.conditions import Key

try:
    from shared.db import get_table
    from shared.utils import get_utc_iso
except ImportError:
    from ..shared.db import get_table
    from ..shared.utils import get_utc_iso

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
ACTIVE_STATUSES = ["OPEN", "ASSIGNED", "IN_PROGRESS"]


def get_sns_client() -> Any:
    """Returns Boto3 SNS client."""
    return boto3.client("sns", region_name=AWS_REGION)


def format_sns_message(incident: Dict[str, Any]) -> str:
    """Formats an executive maintenance escalation alert for campus administrators."""
    return f"""=======================================================
CAMPUSOPS AUTOMATED SLA BREACH ALERT
=======================================================

An active campus incident has exceeded its defined SLA resolution target.

Incident ID : {incident.get('incident_id')}
Title       : {incident.get('title')}
Priority    : {incident.get('priority')} (Target: {incident.get('sla_hours')} hours)
Category    : {incident.get('category')}
Location    : {incident.get('location')}
Current Status: {incident.get('status')}
Reported By : {incident.get('created_by_name')}
Reported At : {incident.get('created_at')}
SLA Target  : {incident.get('sla_deadline')}
Assigned To : {incident.get('assigned_to_name', 'UNASSIGNED - Requires Immediate Attention!')}

Action Required:
Please log in to the CampusOps Administrative Portal to escalate or allocate emergency technicians.
"""


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point invoked on a recurring schedule by Amazon EventBridge.
    """
    table = get_table()
    sns_client = get_sns_client()
    now_iso = get_utc_iso()

    breached_incidents: List[Dict[str, Any]] = []

    # 1. Query each active status partition using StatusGSI
    for status in ACTIVE_STATUSES:
        try:
            # Query StatusGSI for tickets where status = :status and sla_deadline <= :now
            response = table.query(
                IndexName="StatusGSI",
                KeyConditionExpression=Key("status").eq(status) & Key("sla_deadline").lte(now_iso)
            )
            items = response.get("Items", [])

            for item in items:
                # 2. Check if already marked BREACHED to prevent duplicate spam notifications
                if item.get("sla_status") != "BREACHED":
                    incident_id = item["incident_id"]

                    # 3. Update DynamoDB: mark sla_status as BREACHED
                    table.update_item(
                        Key={"incident_id": incident_id},
                        UpdateExpression="SET #sla_status = :b, #updated_at = :ua",
                        ExpressionAttributeNames={
                            "#sla_status": "sla_status",
                            "#updated_at": "updated_at"
                        },
                        ExpressionAttributeValues={
                            ":b": "BREACHED",
                            ":ua": now_iso
                        }
                    )

                    # 4. Dispatch SNS email notification if SNS_TOPIC_ARN is configured
                    if SNS_TOPIC_ARN:
                        subject = f"[CampusOps SLA BREACH] {item.get('priority')} Issue in {item.get('location')}"
                        sns_client.publish(
                            TopicArn=SNS_TOPIC_ARN,
                            Subject=subject[:100], # Subject max length constraint
                            Message=format_sns_message(item)
                        )

                    breached_incidents.append(item)

        except Exception as e:
            print(f"Error checking SLA for status {status}: {str(e)}")

    return {
        "status": "SUCCESS",
        "timestamp": now_iso,
        "breached_count": len(breached_incidents),
        "breached_ids": [b.get("incident_id") for b in breached_incidents]
    }

