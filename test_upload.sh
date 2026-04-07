#!/bin/bash

# Test Upload Endpoint

echo "🧪 Testing Upload Endpoint"
echo "=========================="
echo ""

# Create a test file
echo "Creating test exam file..."
TEST_FILE="/tmp/test_exam.txt"
cat > "$TEST_FILE" << 'EOF'
Question 1: What is photosynthesis?
Student Answer: Plants use sunlight to make food
Expected Answer: Photosynthesis is the process by which plants use sunlight, water, and CO2 to create glucose and oxygen through chemical reactions in chlorophyll.

Question 2: Explain the water cycle.
Student Answer: Water evaporates and forms clouds
Expected Answer: The water cycle involves evaporation (water becomes vapor), condensation (vapor becomes clouds), precipitation (water falls), and collection (water returns to oceans/lakes).
EOF

echo "✅ Test file created: $TEST_FILE"
echo ""

# Test 1: Basic POST (should fail - no file)
echo "Test 1: POST without file"
curl -X POST http://127.0.0.1:8000/api/exams/upload/ \
  -H "Content-Type: application/json" \
  2>/dev/null | jq '.' 2>/dev/null || echo "Failed to parse response"
echo ""

# Test 2: POST with file
echo "Test 2: POST with file (FormData)"
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/exams/upload/ \
  -F "file=@$TEST_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

echo "HTTP Status: $HTTP_CODE"
echo "Response:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

# Test 3: CORS Preflight
echo "Test 3: CORS Preflight (OPTIONS)"
CORS_RESPONSE=$(curl -s -v -X OPTIONS http://127.0.0.1:8000/api/exams/upload/ \
  -H "Origin: http://localhost:3000" 2>&1 | grep "access-control")

if [ -z "$CORS_RESPONSE" ]; then
  echo "❌ No CORS headers found"
else
  echo "✅ CORS headers present:"
  echo "$CORS_RESPONSE"
fi

echo ""
echo "✅ Tests complete!"
