#!/usr/bin/env bash
# A4: curl examples for the local ADK API server.
#
# Prerequisites:
#   uv run adk api_server a4_deployment
#
# Run from repo root:
#   bash a4_deployment/curl_examples.sh

BASE="http://localhost:8000"
APP="a4_deployment"
USER="instructor"

echo "=== 1. List available apps ==="
curl -s "$BASE/list-apps" | python3 -m json.tool

echo ""
echo "=== 2. Create a session ==="
SESSION=$(curl -s -X POST "$BASE/apps/$APP/users/$USER/sessions" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Session ID: $SESSION"

echo ""
echo "=== 3. Run — returns and store hours ==="
curl -s -X POST "$BASE/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_name\": \"$APP\",
    \"user_id\": \"$USER\",
    \"session_id\": \"$SESSION\",
    \"new_message\": {
      \"role\": \"user\",
      \"parts\": [{\"text\": \"What's your return policy and are you open on Sundays?\"}]
    }
  }" | python3 -m json.tool

echo ""
echo "=== 4. Run — streaming (SSE) ==="
curl -s -N -X POST "$BASE/run_sse" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_name\": \"$APP\",
    \"user_id\": \"$USER\",
    \"session_id\": \"$SESSION\",
    \"new_message\": {
      \"role\": \"user\",
      \"parts\": [{\"text\": \"What payment methods do you accept?\"}]
    }
  }" | head -20
