# 🚀 Quick Reference Card

## Essential Commands

### Start Development Server
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
**Access**: http://localhost:8000

### Create Superuser
```powershell
python manage.py createsuperuser
```

### Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Start Celery Worker
```powershell
celery -A exam_checker worker --loglevel=info --pool=solo
```

### Docker Commands
```powershell
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f web

# Stop all
docker-compose down

# Run migrations
docker-compose exec web python manage.py migrate
```

## 📡 Key API Endpoints

### Authentication
| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/users/register/` | POST | ❌ |
| `/api/users/login/` | POST | ❌ |
| `/api/users/profile/` | GET | ✅ |

### Exams
| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/exams/upload/` | POST | Optional |
| `/api/exams/` | GET | ✅ |
| `/api/exams/{id}/` | GET | ✅ |

### Evaluations
| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/evaluations/evaluate/{id}/` | POST | Optional |
| `/api/evaluations/` | GET | ✅ |
| `/api/evaluations/{id}/` | GET | ✅ |

## 🔐 Environment Variables (Required)

```env
# CRITICAL - Must add your own key!
OPENAI_API_KEY=your-key-here

# Optional (has defaults)
DEBUG=True
SECRET_KEY=auto-generated
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `SETUP_GUIDE.md` | Step-by-step setup |
| `API_TESTING.md` | API examples |
| `sample_data/` | Test data |

## 🧪 Testing Workflow

1. **Register User**
```json
POST /api/users/register/
{
    "email": "test@test.com",
    "name": "Test User",
    "password": "Test123!",
    "password_confirm": "Test123!"
}
```

2. **Login & Get Token**
```json
POST /api/users/login/
{
    "email": "test@test.com",
    "password": "Test123!"
}
```

3. **Upload Exam**
```
POST /api/exams/upload/
Authorization: Bearer <token>
Body: form-data with file
```

4. **Evaluate**
```json
POST /api/evaluations/evaluate/1/
Authorization: Bearer <token>
Body: See sample_data/evaluation_request.json
```

## 🔧 Troubleshooting

### "OpenAI API Error"
➡️ Add your API key to `.env`

### "Module not found"
➡️ `pip install -r requirements.txt`

### "Port 8000 in use"
➡️ `python manage.py runserver 8001`

### "Tesseract not found"
➡️ Install Tesseract or use .txt files only

## 📊 Project Statistics

- **Django Apps**: 3
- **AI Modules**: 6
- **API Endpoints**: 15+
- **Models**: 5
- **Status**: ✅ COMPLETE

## 🎯 Evaluation Formula

```
Final Score = (0.6 × SBERT) + (0.4 × GPT)
```

- **SBERT**: Semantic similarity (0-100)
- **GPT**: Contextual analysis (0-100)
- **Result**: Combined score (0-100) + Grade (A+ to F)

## 📞 Quick Links

- **Admin Panel**: http://localhost:8000/admin
- **Sample Data**: `sample_data/`
- **Logs**: `logs/errors.log`
- **Media Files**: `media/`

## ⚡ Performance Targets

- Evaluation: < 10 seconds
- OCR: < 5 seconds/page
- Accuracy: 90% vs human
- Variance: ±5%

## 🎓 Academic Components

✅ Hybrid AI Methodology
✅ Full-stack Implementation
✅ RESTful API
✅ Production Deployment
✅ Security Best Practices
✅ Comprehensive Documentation

---

**Remember**: Add your OpenAI API key before testing evaluations!

**For detailed help**: See README.md or SETUP_GUIDE.md
