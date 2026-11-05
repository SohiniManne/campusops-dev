"""
Shared Business Logic Utilities: SLA Calculation, Timestamps, and Validations.
Purpose: Encapsulates priority SLA rules, date formatting, and input validation for incidents.
"""

from datetime import datetime, timezone, timedelta
import uuid
from typing import Tuple, Dict, Any, Optional

# Priority-to-Resolution-Window mapping (hours)
SLA_HOURS_MAP: Dict[str, int] = {
    "CRITICAL": 1,
    "HIGH": 4,
    "MEDIUM": 12,
    "LOW": 24
}

# Allowed Incident Categories
ALLOWED_CATEGORIES = [
    "ELECTRICAL",
    "PLUMBING",
    "WIFI_NETWORK",
    "LAB_EQUIPMENT",
    "CLASSROOM_INFRA",
    "OTHER"
]

# Allowed Incident Status Values
ALLOWED_STATUSES = [
    "OPEN",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED"
]


def get_utc_now() -> datetime:
    """Returns current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def get_utc_iso(dt: Optional[datetime] = None) -> str:
    """Returns ISO 8601 UTC string format: YYYY-MM-DDTHH:MM:SSZ."""
    if dt is None:
        dt = get_utc_now()
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(iso_str: str) -> datetime:
    """Parses an ISO 8601 UTC string into a timezone-aware datetime."""
    if iso_str.endswith("Z"):
        iso_str = iso_str[:-1] + "+00:00"
    return datetime.fromisoformat(iso_str)


def calculate_sla_deadline(priority: str, created_at: Optional[datetime] = None) -> Tuple[int, str]:
    """
    Calculates SLA resolution window in hours and ISO 8601 deadline timestamp.
    
    Args:
        priority: One of CRITICAL (1h), HIGH (4h), MEDIUM (12h), LOW (24h)
        created_at: Datetime incident was submitted (defaults to now)
        
    Returns:
        tuple[int, str]: (sla_hours, sla_deadline_iso)
    """
    if created_at is None:
        created_at = get_utc_now()
    
    hours = SLA_HOURS_MAP.get(priority.upper(), 24)
    deadline = created_at + timedelta(hours=hours)
    return hours, get_utc_iso(deadline)


def generate_incident_id() -> str:
    """
    Generates a unique readable incident ID formatted as inc-YYYYMMDD-hex.
    Example: inc-20261105-3b9e4a
    """
    date_part = get_utc_now().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6]
    return f"inc-{date_part}-{unique_suffix}"


def validate_incident_input(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates payload fields when creating an incident.
    
    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object"

    title = data.get("title")
    if not title or not isinstance(title, str) or len(title.strip()) < 3 or len(title) > 100:
        return False, "Title is required and must be between 3 and 100 characters"

    description = data.get("description")
    if not description or not isinstance(description, str) or len(description.strip()) < 5 or len(description) > 1000:
        return False, "Description is required and must be between 5 and 1000 characters"

    location = data.get("location")
    if not location or not isinstance(location, str) or len(location.strip()) < 2 or len(location) > 100:
        return False, "Location is required and must be between 2 and 100 characters"

    category = data.get("category")
    if not category or category.upper() not in ALLOWED_CATEGORIES:
        return False, f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}"

    priority = data.get("priority")
    if not priority or priority.upper() not in SLA_HOURS_MAP:
        return False, f"Priority must be one of: {', '.join(SLA_HOURS_MAP.keys())}"

    return True, None

