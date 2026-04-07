#!/bin/bash

# ============================================================================
# AI POWERED EXAM CHECKER - COMPREHENSIVE STARTUP SCRIPT
# ============================================================================
# This script starts both backend and frontend services
# Usage: ./start_server.sh
# ============================================================================

set -e  # Exit on error

PROJECT_DIR="/Users/macbookpro/Downloads/AI Powered Exam Checker/AI-Powered-Exam-Checker"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}================================================${NC}"
echo -e "${GREEN}  AI Powered Exam Checker - Server Startup${NC}"
echo -e "${YELLOW}================================================${NC}\n"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Kill any existing processes
echo -e "${YELLOW}[1/6] Cleaning up old processes...${NC}"
pkill -f "runserver" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Old processes stopped${NC}\n"

# Verify environment
echo -e "${YELLOW}[2/6] Verifying environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    exit 1
fi
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}\n"

# Check Tesseract
echo -e "${YELLOW}[3/6] Verifying Tesseract OCR...${NC}"
if which tesseract >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Tesseract installed: $(which tesseract)${NC}"
else
    echo -e "${RED}⚠️  Tesseract not found in PATH${NC}"
    echo "   Install with: brew install tesseract"
fi
echo ""

# Check Django
echo -e "${YELLOW}[4/6] Checking Django configuration...${NC}"
python3 manage.py check 2>&1 | grep -E "(System check|ERROR)" | head -1
echo -e "${GREEN}✅ Django configuration OK${NC}\n"

# Start Backend
echo -e "${YELLOW}[5/6] Starting backend server...${NC}"
echo "   Command: python3 manage.py runserver 0.0.0.0:8000"
nohup python3 manage.py runserver 0.0.0.0:8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    echo "   Access: http://localhost:8000/api"
else
    echo -e "${RED}❌ Failed to start backend${NC}"
    exit 1
fi
echo ""

# Start Frontend
echo -e "${YELLOW}[6/6] Starting frontend server...${NC}"
cd frontend
echo "   Command: npm start"
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo "   Access: http://localhost:3000"
else
    echo -e "${RED}❌ Failed to start frontend${NC}"
    exit 1
fi

cd ..

# Final summary
echo -e "\n${YELLOW}================================================${NC}"
echo -e "${GREEN}   ✅ SERVERS STARTED SUCCESSFULLY${NC}"
echo -e "${YELLOW}================================================${NC}\n"

echo -e "${GREEN}📌 SERVICE ENDPOINTS:${NC}"
echo -e "   Backend API:  ${YELLOW}http://localhost:8000/api${NC}"
echo -e "   Frontend UI:  ${YELLOW}http://localhost:3000${NC}"
echo -e "   Admin Panel:  ${YELLOW}http://localhost:8000/admin${NC}\n"

echo -e "${GREEN}📋 QUICK REFERENCE:${NC}"
echo -e "   Backend Test:    curl http://localhost:8000/api/exams/upload/"
echo -e "   Frontend Test:   curl http://localhost:3000"
echo -e "   Stop Backend:    pkill -f 'runserver'"
echo -e "   Stop Frontend:   pkill -f 'npm start'"
echo -e "   Backend Logs:    tail -f logs/backend.log"
echo -e "   Frontend Logs:   tail -f logs/frontend.log\n"

echo -e "${GREEN}🎯 NEXT STEPS:${NC}"
echo -e "   1. Open browser to ${YELLOW}http://localhost:3000${NC}"
echo -e "   2. Upload an exam file (PDF, TXT, JPG, or PNG)"
echo -e "   3. Review extracted questions"
echo -e "   4. Add expected answers"
echo -e "   5. Click Evaluate and see results\n"

echo -e "${GREEN}⚠️  IMPORTANT:${NC}"
echo -e "   • Keep this terminal open - servers run here"
echo -e "   • To stop servers: Ctrl+C or use: pkill -f 'runserver && npm'"
echo -e "   • Check logs if anything fails: logs/backend.log or logs/frontend.log"
echo -e "   • Claude API key must be set in .env file\n"
