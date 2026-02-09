# AI-Powered Exam Checker - Setup and Run Guide

## Quick Start Guide

### Prerequisites
✅ Python 3.10+ installed
✅ Virtual environment `venv` created
✅ Django installed in venv
✅ Git initialized

### Step 1: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Install All Dependencies
```powershell
pip install -r requirements.txt
```

**Note**: This may take 10-15 minutes as it downloads AI models and dependencies.

### Step 3: Configure Environment Variables

1. Your `.env` file is already created. **IMPORTANT**: Add your OpenAI API key:

```env
OPENAI_API_KEY=your-actual-openai-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### Step 4: Install Tesseract OCR (for handwritten text extraction)

**Windows**:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. The path is already configured in `.env`

**Skip Tesseract if you're only testing with typed text files**

### Step 5: Run Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Admin User (Superuser)
```powershell
python manage.py createsuperuser
```

Enter:
- Email: admin@example.com
- Name: Admin
- Password: (your choice)

### Step 7: Create Media and Logs Directories
```powershell
New-Item -ItemType Directory -Force -Path media
New-Item -ItemType Directory -Force -Path logs
```

### Step 8: Run the Development Server
```powershell
python manage.py runserver
```

✅ **Backend API is now running at: http://localhost:8000**

### Step 9: Test the Admin Panel

Open browser: http://localhost:8000/admin
Login with superuser credentials

## Testing the API

### Option 1: Using PowerShell (Example user registration)

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    email = "test@example.com"
    name = "Test User"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/users/register/" -Method Post -Headers $headers -Body $body
```

### Option 2: Using Postman or Thunder Client (VS Code)

Import this collection:

**1. Register User**
- POST: `http://localhost:8000/api/users/register/`
- Body (JSON):
```json
{
    "email": "student@example.com",
    "name": "John Doe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
}
```

**2. Login**
- POST: `http://localhost:8000/api/users/login/`
- Body (JSON):
```json
{
    "email": "student@example.com",
    "password": "SecurePass123!"
}
```

**3. Upload Exam (copy access_token from login response)**
- POST: `http://localhost:8000/api/exams/upload/`
- Headers: `Authorization: Bearer <your_access_token>`
- Body (form-data):
  - file: (select a PDF/TXT/image file)

**4. Evaluate Exam**
- POST: `http://localhost:8000/api/evaluations/evaluate/1/`
- Headers: 
  - `Authorization: Bearer <your_access_token>`
  - `Content-Type: application/json`
- Body (JSON):
```json
{
    "questions": [
        {
            "question_number": 1,
            "question_text": "What is machine learning?",
            "student_answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make decisions.",
            "model_answer": "Machine learning is a branch of artificial intelligence focused on building systems that learn from data. It involves training algorithms on data to make predictions or decisions without explicit programming for each task."
        }
    ]
}
```

## Optional: Running with Celery (Async Processing)

### Terminal 1: Start Redis (using Docker)
```powershell
docker run -d -p 6379:6379 redis:7-alpine
```

### Terminal 2: Start Celery Worker
```powershell
.\venv\Scripts\Activate.ps1
celery -A exam_checker worker --loglevel=info --pool=solo
```

### Terminal 3: Start Django Server
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

## System Architecture

```
┌─────────────────┐
│   React App     │ (Frontend - Optional)
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST API
         ▼
┌─────────────────┐
│  Django + DRF   │ (Backend API)
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────────────────────┐
    │                         │
    ▼                         ▼
┌──────────┐          ┌──────────────┐
│PostgreSQL│          │  AI Engine   │
│   DB     │          │ SBERT + GPT  │
└──────────┘          └──────────────┘
                              │
                      ┌───────┴────────┐
                      │                │
                      ▼                ▼
                 ┌─────────┐    ┌──────────┐
                 │  Redis  │    │   OCR    │
                 │ Celery  │    │Tesseract │
                 └─────────┘    └──────────┘
```

## Project Status Checklist

✅ Django project created
✅ Database models defined (Users, Exams, Evaluations)
✅ AI Evaluation Engine (SBERT + GPT) implemented
✅ OCR module for handwritten text
✅ REST API endpoints created
✅ JWT authentication implemented
✅ Celery async processing configured
✅ Docker deployment files created
✅ Admin panel configured
✅ Exception handling implemented
✅ Logging configured

## Next Steps

1. ✅ **Test API endpoints** using Postman/Thunder Client
2. ✅ **Add your OpenAI API key** to `.env`
3. ⚠️ **Create React frontend** (optional - API is fully functional)
4. ⚠️ **Deploy to production** using Docker Compose

## Troubleshooting

### "OpenAI API Error"
➡️ Make sure you added your actual API key in `.env`:
```env
OPENAI_API_KEY=sk-proj-...your-actual-key...
```

### "Tesseract not found"
➡️ Install Tesseract OCR or skip OCR testing and use `.txt` or typed `.pdf` files

### "Module not found" errors
➡️ Make sure venv is activated and run:
```powershell
pip install -r requirements.txt
```

### "Port 8000 already in use"
➡️ Stop other Django servers or use a different port:
```powershell
python manage.py runserver 8001
```

## Important Notes

🔴 **REQUIRED**: OpenAI API Key - You MUST add your API key to `.env` for evaluation to work
🟡 **OPTIONAL**: Tesseract OCR - Only needed for scanned/handwritten exams
🟡 **OPTIONAL**: Redis + Celery - For async processing (recommended for production)
🟡 **OPTIONAL**: PostgreSQL - SQLite works fine for development

## Key Files Location

- **Settings**: `exam_checker/settings.py`
- **Environment**: `.env`
- **API URLs**: `exam_checker/urls.py`
- **Models**: `users/models.py`, `exams/models.py`, `evaluations/models.py`
- **AI Engine**: `exam_checker/ai_engine/`
- **Admin**: `http://localhost:8000/admin`

## Support

Need help? Check:
1. README.md (comprehensive documentation)
2. Code comments (detailed explanations)
3. Django logs in `logs/` directory
4. Console output for errors

---

**Ready to test!** Start with the admin panel, then test API endpoints with Postman/Thunder Client.

**Remember**: Add your OpenAI API key before evaluating exams!
