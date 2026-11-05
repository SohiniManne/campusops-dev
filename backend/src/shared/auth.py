"""
Shared Authentication and Role-Based Access Control (RBAC) Helper.
AWS Resource: Amazon Cognito Claims Extractor.
Purpose: Validates Cognito JWT claims passed by API Gateway authorizer and enforces user group permissions.
"""

from typing import Dict, List, Any


def get_user_info(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts authenticated user ID, email/username, and Cognito groups from API Gateway request context.
    
    Cognito User Pool Authorizer injects verified JWT claims into:
    event['requestContext']['authorizer']['claims']
    """
    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}
    claims = authorizer.get("claims") or {}

    # Extract user ID (Cognito sub claim is unique immutable UUID per user)
    user_id = claims.get("sub") or claims.get("cognito:username") or "anonymous"
    
    # Extract email or display username
    email = claims.get("email") or claims.get("cognito:username") or user_id
    
    # Extract groups (can be a comma-separated string e.g. 'Student,Admin' or a Python list)
    groups_claim = claims.get("cognito:groups") or []
    if isinstance(groups_claim, str):
        groups = [g.strip() for g in groups_claim.split(",") if g.strip()]
    elif isinstance(groups_claim, list):
        groups = [str(g).strip() for g in groups_claim if str(g).strip()]
    else:
        groups = []

    return {
        "user_id": user_id,
        "email": email,
        "groups": groups
    }


def is_in_group(user_info: Dict[str, Any], allowed_groups: List[str]) -> bool:
    """
    Checks if user belongs to any of the allowed Cognito groups (case-insensitive).
    
    Args:
        user_info: Dictionary containing 'groups' list
        allowed_groups: List of permitted group names (e.g. ['Admin', 'Staff'])
        
    Returns:
        bool: True if authorized, False otherwise
    """
    user_groups = user_info.get("groups", [])
    allowed_lower = {group.lower() for group in allowed_groups}
    return any(user_group.lower() in allowed_lower for user_group in user_groups)

