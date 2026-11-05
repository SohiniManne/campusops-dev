#!/usr/bin/env bash
BASE_URL="https://lp0jvwl5f9.execute-api.ap-south-1.amazonaws.com/dev"
TEST_ID="test-check-only"

test_route() {
  local method="$1"
  local path="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$path")
  echo "$path | $method | $code"
}

echo "Route | Method | Status Code"
echo "---|---|---"
test_route "GET" "/incidents"
test_route "POST" "/incidents"
test_route "OPTIONS" "/incidents"
test_route "GET" "/incidents/$TEST_ID"
test_route "OPTIONS" "/incidents/$TEST_ID"
test_route "POST" "/incidents/$TEST_ID/assign"
test_route "OPTIONS" "/incidents/$TEST_ID/assign"
test_route "PATCH" "/incidents/$TEST_ID/status"
test_route "OPTIONS" "/incidents/$TEST_ID/status"
test_route "POST" "/incidents/$TEST_ID/resolve"
test_route "OPTIONS" "/incidents/$TEST_ID/resolve"

