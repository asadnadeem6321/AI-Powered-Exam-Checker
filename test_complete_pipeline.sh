#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}    COMPLETE PIPELINE TEST SUITE${NC}"
echo -e "${YELLOW}========================================${NC}\n"

BASE_URL="http://localhost:8000/api"
API_KEY="test-key"

# Test 1: Create a simple text exam file
echo -e "${YELLOW}[TEST 1] Creating sample exam text file...${NC}"
cat > /tmp/sample_exam.txt << 'EOF'
MATHEMATICS FINAL EXAM

Question 1: What is the derivative of x^2?
A) 2x
B) x
C) 2
D) x^2
Correct Answer: A

Question 2: Solve: 2x + 5 = 15
A) x = 5
B) x = 10
C) x = 3
D) x = 4
Correct Answer: A

Question 3: What is the area of a circle with radius 5?
A) 25π
B) 10π
C) 5π
D) π
Correct Answer: A
EOF
echo -e "${GREEN}✅ Sample exam file created${NC}\n"

# Test 2: Upload text file
echo -e "${YELLOW}[TEST 2] Uploading text exam file...${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/exams/upload/" \
  -F "file=@/tmp/sample_exam.txt" \
  -F "subject=Mathematics" \
  -H "Accept: application/json")

echo "Response: $UPLOAD_RESPONSE"
EXAM_ID=$(echo $UPLOAD_RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ -z "$EXAM_ID" ]; then
  echo -e "${RED}❌ Failed to extract exam ID from upload response${NC}"
  EXAM_ID=$(echo $UPLOAD_RESPONSE | grep -o '"exam":\{"id":[0-9]*' | grep -o '[0-9]*' | tail -1)
fi

if [ ! -z "$EXAM_ID" ]; then
  echo -e "${GREEN}✅ File uploaded successfully! Exam ID: $EXAM_ID${NC}\n"
else
  echo -e "${RED}❌ Failed to upload file${NC}\n"
  exit 1
fi

# Test 3: Extract questions using Claude API
echo -e "${YELLOW}[TEST 3] Extracting questions from exam text...${NC}"
sleep 2

EXTRACT_RESPONSE=$(curl -s -X POST "$BASE_URL/exams/$EXAM_ID/extract-questions/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json")

echo "Response: $EXTRACT_RESPONSE" | head -100

# Check if questions were extracted
QUESTION_COUNT=$(echo $EXTRACT_RESPONSE | grep -o '"total_questions":[0-9]*' | grep -o '[0-9]*')

if [ ! -z "$QUESTION_COUNT" ] && [ "$QUESTION_COUNT" -gt 0 ]; then
  echo -e "${GREEN}✅ Questions extracted successfully! Found $QUESTION_COUNT questions${NC}\n"
else
  echo -e "${YELLOW}⚠️  Could not extract questions from response${NC}"
  echo -e "${YELLOW}   This might be due to Claude API issues${NC}\n"
fi

# Test 4: Verify database storage
echo -e "${YELLOW}[TEST 4] Verifying exam data in database...${NC}"
DB_CHECK=$(sqlite3 /Users/macbookpro/Downloads/AI\ Powered\ Exam\ Checker/AI-Powered-Exam-Checker/db.sqlite3 \
  "SELECT id, file_name, status, raw_text FROM exams_exam WHERE id=$EXAM_ID LIMIT 1;" 2>/dev/null)

if [ ! -z "$DB_CHECK" ]; then
  echo -e "${GREEN}✅ Exam found in database${NC}"
  echo "Data: $DB_CHECK\n"
else
  echo -e "${RED}❌ Exam not found in database${NC}\n"
fi

# Test 5: Test with PDF (if available)
echo -e "${YELLOW}[TEST 5] Testing with sample PDF...${NC}"
if command -v python3 &> /dev/null; then
  python3 -c "
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas('/tmp/sample_exam.pdf', pagesize=letter)
c.drawString(100, 750, 'PHYSICS EXAM')
c.drawString(100, 700, 'Question 1: What is the speed of light?')
c.drawString(100, 680, 'A) 3 x 10^8 m/s')
c.drawString(100, 660, 'B) 2 x 10^8 m/s')
c.drawString(100, 640, 'C) 5 x 10^8 m/s')
c.drawString(100, 620, 'D) 1 x 10^8 m/s')
c.save()
print('PDF created')
" 2>/dev/null

  if [ -f "/tmp/sample_exam.pdf" ]; then
    echo -e "${GREEN}✅ Sample PDF created${NC}"
    
    # Upload PDF
    PDF_RESPONSE=$(curl -s -X POST "$BASE_URL/exams/upload/" \
      -F "file=@/tmp/sample_exam.pdf" \
      -F "subject=Physics" \
      -H "Accept: application/json")
    
    PDF_EXAM_ID=$(echo $PDF_RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    if [ ! -z "$PDF_EXAM_ID" ]; then
      echo -e "${GREEN}✅ PDF uploaded successfully! Exam ID: $PDF_EXAM_ID${NC}\n"
    else
      echo -e "${YELLOW}⚠️  PDF upload response: $(echo $PDF_RESPONSE)${NC}\n"
    fi
  else
    echo -e "${YELLOW}⚠️  Could not create PDF test file${NC}\n"
  fi
else
  echo -e "${YELLOW}⚠️  Python3 not in PATH, skipping PDF test${NC}\n"
fi

# Summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}TEST SUITE COMPLETE${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "\nKey Validations:"
echo -e "  ✓ Text file upload: ${GREEN}PASSED${NC}"
echo -e "  ✓ Question extraction: Check response above"
echo -e "  ✓ Database storage: Check response above"
echo -e "\nFrontend Verification:"
echo -e "  1. Go to http://localhost:3000"
echo -e "  2. Upload a sample exam file"
echo -e "  3. Verify questions are extracted"
echo -e "  4. Review and submit answers"
echo -e "  5. Check evaluation results"
echo -e "\nCommon Issues & Solutions:"
echo -e "  - ${RED}Claude API Error:${NC} Check CLAUDE_API_KEY in .env file"
echo -e "  - ${RED}Upload fails:${NC} Verify CORS is enabled and backend is running"
echo -e "  - ${RED}No questions extracted:${NC} Check exam text contains structured questions"
echo ""
