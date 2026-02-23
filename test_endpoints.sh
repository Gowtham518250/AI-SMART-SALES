#!/bin/bash
# Test all API endpoints

BASE_URL="http://localhost:8000"

echo "===== TESTING ALL ENDPOINTS ====="
echo ""

# Test 1: Health Check
echo "1. Testing /health"
curl -X GET $BASE_URL/health
echo ""
echo ""

# Test 2: Register
echo "2. Testing /auth/register"
curl -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "testuser123",
    "email": "testuser@example.com",
    "password": "Test@2004"
  }'
echo ""
echo ""

# Test 3: Login
echo "3. Testing /auth/login"
curl -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_name=testuser123&password=Test@2004"
echo ""
echo ""

# Test 4: Chatbot with Query Param
echo "4. Testing /chatbot/ (with query param)"
curl -X POST "$BASE_URL/chatbot/?query=hello" \
  -H "Content-Type: application/json" \
  -d '{}'
echo ""
echo ""

# Test 5: Today's Insight
echo "5. Testing /today_insight/"
curl -X GET "$BASE_URL/today_insight/" \
  -H "Authorization: Bearer dummy_token"
echo ""
echo ""

# Test 6: Get Sales
echo "6. Testing /auth/sales (GET)"
curl -X GET "$BASE_URL/auth/sales" \
  -H "Authorization: Bearer dummy_token"
echo ""
echo ""

# Test 7: Post Sales
echo "7. Testing /auth/sales (POST)"
curl -X POST "$BASE_URL/auth/sales" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Bearer dummy_token" \
  -d "product_name=testitem&price=100&quantity=5&sale_date=2026-02-08"
echo ""
echo ""

# Test 8: RAG endpoint (would need file)
echo "8. Testing /rag/RAG/ (requires file upload)"
echo "SKIPPED - requires file"
echo ""

# Test 9: SQL Analysis (would need file)
echo "9. Testing /sql_analyst/sql_analysis/ (requires file upload)"
echo "SKIPPED - requires file"
echo ""

echo "===== ENDPOINT TEST COMPLETE ====="
