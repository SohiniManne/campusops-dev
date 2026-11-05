#!/usr/bin/env python3
"""
Smoke test suite for live CampusOps deployment in AWS ap-south-1.
Tests:
1. Unauthenticated requests return 401 Unauthorized.
2. Creates Student test user in Cognito and assigns to 'Student' group.
3. Authenticates as Student and acquires live Cognito JWT.
4. Creates incident via live API Gateway -> Lambda -> DynamoDB (HTTP 201).
5. Confirms Student cannot call Admin routes (assign staff) (HTTP 403).
"""

import json
import os
import secrets
import string
import urllib.request
import urllib.error
import subprocess
import sys

API_URL = "https://lp0jvwl5f9.execute-api.ap-south-1.amazonaws.com/dev"
USER_POOL_ID = "ap-south-1_UmR09agC8"
CLIENT_ID = "3037at1btmphctj8j46a85gg79"
TEST_STUDENT_EMAIL = os.environ.get("TEST_STUDENT_EMAIL", "test.student@campusops.edu")
TEST_PASSWORD = os.environ.get("TEST_STUDENT_PASSWORD") or ("Temp#" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16)))

def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\nStderr: {result.stderr}")
    return result.stdout.strip()

def test_frontend_website():
    print("\n--- Test 0: Verifying S3 Static Website Hosting ---")
    frontend_url = "http://campusops-frontend-dev-c0cf6c4c.s3-website.ap-south-1.amazonaws.com"
    req = urllib.request.Request(frontend_url)
    try:
        res = urllib.request.urlopen(req)
        content = res.read().decode()
        print(f"Status Code: {res.status} (Expected 200)")
        assert res.status == 200, f"Expected 200, got {res.status}"
        assert "<html" in content or "CampusOps" in content or "<title>" in content
        print("PASS: Frontend website is live and accessible at S3 website endpoint.")
    except Exception as e:
        print(f"FAILED: Frontend check error: {e}")
        raise e

def test_unauthenticated():
    print("\n--- Test 1: Unauthenticated request to /incidents ---")
    req = urllib.request.Request(f"{API_URL}/incidents")
    try:
        urllib.request.urlopen(req)
        print("FAILED: Unauthenticated request succeeded unexpectedly!")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"Status Code: {e.code} (Expected 401)")
        body = e.read().decode()
        print(f"Response: {body}")
        assert e.code == 401, f"Expected 401, got {e.code}"
        print("PASS: API Gateway Cognito Authorizer rejected unauthenticated request with 401.")

def setup_student_user():
    print("\n--- Test 2: Provisioning Student test user in Cognito ---")
    # Check if user already exists, or create
    try:
        run_cmd(f'aws cognito-idp admin-create-user --user-pool-id {USER_POOL_ID} --username "{TEST_STUDENT_EMAIL}" --user-attributes Name=email,Value="{TEST_STUDENT_EMAIL}" Name=email_verified,Value=true --message-action SUPPRESS')
        print(f"Created Cognito user: {TEST_STUDENT_EMAIL}")
    except RuntimeError as e:
        if "UsernameExistsException" in str(e):
            print(f"User {TEST_STUDENT_EMAIL} already exists in User Pool.")
        else:
            raise e

    # Set permanent password
    run_cmd(f'aws cognito-idp admin-set-user-password --user-pool-id {USER_POOL_ID} --username "{TEST_STUDENT_EMAIL}" --password "{TEST_PASSWORD}" --permanent')
    print("Set permanent password.")

    # Add user to Student group
    run_cmd(f'aws cognito-idp admin-add-user-to-group --user-pool-id {USER_POOL_ID} --username "{TEST_STUDENT_EMAIL}" --group-name Student')
    print("Added user to 'Student' group.")

def login_student():
    print("\n--- Test 3: Authenticating Student user with Cognito InitiateAuth ---")
    out = run_cmd(f'aws cognito-idp initiate-auth --client-id {CLIENT_ID} --auth-flow USER_PASSWORD_AUTH --auth-parameters USERNAME="{TEST_STUDENT_EMAIL}",PASSWORD="{TEST_PASSWORD}"')
    data = json.loads(out)
    id_token = data["AuthenticationResult"]["IdToken"]
    print("PASS: Acquired cryptographically signed Cognito IdToken (JWT).")
    return id_token

def test_create_incident(id_token):
    print("\n--- Test 4: Creating incident via POST /incidents with Student JWT ---")
    payload = {
        "title": "Broken bench in Lab 101",
        "description": "Front row wooden bench collapsed during afternoon physics lecture.",
        "category": "CLASSROOM_INFRA",
        "priority": "HIGH",
        "location": "Physics Block, Lab 101"
    }
    req = urllib.request.Request(
        f"{API_URL}/incidents",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        res = urllib.request.urlopen(req)
        body = json.loads(res.read().decode())
        print(f"Status Code: {res.status} (Expected 201)")
        print(f"Created Incident ID: {body['incident']['incident_id']}")
        print(f"SLA Deadline: {body['incident']['sla_deadline']}")
        print(f"Status: {body['incident']['status']}")
        assert res.status == 201, f"Expected 201, got {res.status}"
        assert body['incident']['status'] == "OPEN"
        print("PASS: Student successfully created incident in DynamoDB via API Gateway and Lambda.")
        return body['incident']['incident_id']
    except urllib.error.HTTPError as e:
        print(f"FAILED Status Code: {e.code}")
        print(f"Error Response Body: {e.read().decode()}")
        raise e

def test_student_cannot_call_admin_route(id_token, incident_id):
    print("\n--- Test 5: Confirm Student CANNOT call Admin route (assign staff) ---")
    payload = {
        "assigned_to": "usr-ramesh-tech",
        "assigned_to_name": "Ramesh Kumar"
    }
    req = urllib.request.Request(
        f"{API_URL}/incidents/{incident_id}/assign",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        urllib.request.urlopen(req)
        print("FAILED: Student was able to call admin route!")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"Status Code: {e.code} (Expected 403 Forbidden)")
        body = e.read().decode()
        print(f"Response: {body}")
        assert e.code == 403, f"Expected 403, got {e.code}"
        print("PASS: Lambda RBAC strictly blocked Student from assigning staff (HTTP 403 Forbidden).")

if __name__ == "__main__":
    test_frontend_website()
    test_unauthenticated()
    setup_student_user()
    token = login_student()
    inc_id = test_create_incident(token)
    test_student_cannot_call_admin_route(token, inc_id)
    print("\n=============================================")
    print("ALL LIVE SYSTEM SMOKE TESTS PASSED (5/5) ✅")
    print("=============================================")

