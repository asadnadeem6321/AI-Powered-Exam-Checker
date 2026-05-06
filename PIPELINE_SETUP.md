# Backend-Frontend Pipeline Connection - Complete Setup

## ✅ What Was Fixed

### 1. **Backend - Question Extraction Endpoint**
- Created `question_extractor.py` module using Claude API to extract questions from exam text
- Added new endpoint: `POST /api/exams/{exam_id}/extract-questions/`
- Endpoint extracts questions, answers, and metadata using AI

### 2. **Frontend - Question Form Page**
- Created `QuestionFormPage.jsx` for users to review extracted questions
- Allows users to verify/edit questions and add expected answers
- Beautiful form UI with validation

### 3. **Complete Pipeline Flow**
The entire process now works as follows:

```
1. User Authenticates/Logs In
    ↓
2. User Uploads Exam File (PDF, DOCX, JPT, PNG, TXT)
    ↓
3. Backend Extracts Text from File (TextExtractor)
    ↓
4. Frontend Redirects to Question Form Page
    ↓
5. Backend Uses Claude AI to Extract Questions  
    ↓
6. Questions Displayed in Form for User Review
    ↓
7. User Adds Expected Answers & Verifies
    ↓
8. User Clicks "Evaluate & Get Results"
    ↓
9. Backend Sends Questions to Claude API for Evaluation
    ↓
10. Results Displayed on Results Page
    ↓
11. User Sees Detailed Feedback & Scores
```

## 📁 Files Modified/Created

### Backend
- ✅ `exam_checker/ai_engine/question_extractor.py` - NEW: Question extraction using Claude
- ✅ `exam_checker/ai_engine/__init__.py` - Updated: Added QuestionExtractor export
- ✅ `exams/views.py` - Updated: Added extract_questions endpoint
- ✅ `exams/urls.py` - Updated: Added route for question extraction

### Frontend
- ✅ `src/pages/QuestionFormPage.jsx` - NEW: Question review and collection form
- ✅ `src/pages/UploadPage.jsx` - Updated: Navigate to question form after upload
- ✅ `src/App.jsx` - Updated: Added question form route
- ✅ `src/services/examService.js` - Updated: Added extractQuestions method
- ✅ `.env` - NEW: API URL configuration

## 🚀 How to Test

### Step 1: Access the Application
```
Frontend: http://localhost:3000
Backend: http://localhost:8000
```

### Step 2: Register/Login
- Click "Register" to create account OR use guest mode
- Login with credentials

### Step 3: Upload Exam File
- Click "Upload Exam"
- Select a PDF, DOCX, JPG, PNG, or TXT file
- Click "Upload & Continue"

### Step 4: Review Extracted Questions
- System will extract questions using Claude AI
- Review the extracted questions
- **IMPORTANT**: Add expected answers in the "Expected Answer" field
- Verify student answers from the document
- Make any corrections needed

### Step 5: Evaluate
- Click "Evaluate & Get Results"
- Backend will evaluate each answer against model answer
- Results displayed with scores and feedback

### Step 6: View Results
- See detailed evaluation for each question
- View strengths, weaknesses, and suggestions
- See overall score and feedback

## 🔄 API Endpoints

### Exam Upload
```
POST /api/exams/upload/
Content-Type: multipart/form-data
Body: { file: <file> }
Response: { exam: { id, file_name, file_size, ... } }
```

### Extract Questions
```
POST /api/exams/{exam_id}/extract-questions/
Response: {
  data: {
    total_questions: number,
    questions: [
      {
        question_number: 1,
        question_text: "...",
        question_type: "essay|multiple_choice|...",
        student_answer: "...",
        model_answer: null,  // User fills this in
        options: [...] // for multiple choice
      }
    ],
    metadata: {...}
  }
}
```

### Evaluate Exam
```
POST /api/evaluations/evaluate/{exam_id}/
Body: {
  questions: [
    {
      question_number: 1,
      question_text: "...",
      student_answer: "...",
      model_answer: "..."
    }
  ]
}
Response: { evaluation: {...}, message: "..." }
```

## 🔧 Configuration

### Backend (.env)
```
CLAUDE_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=2000
CLAUDE_TEMPERATURE=0.7
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## 📊 Data Flow

### Upload Flow
```
File Upload
    ↓
Save to Exam model
    ↓
Extract text using TextExtractor (OCR + file parsing)
    ↓
Save raw_text to database
    ↓
Return exam object to frontend
```

### Question Extraction Flow
```
Frontend requests extraction
    ↓
Backend loads exam raw_text
    ↓
Send to Claude API with extraction prompt
    ↓
Claude extracts questions structure
    ↓
Validate extracted data
    ↓
Return to frontend
```

### Evaluation Flow
```
User fills questions form
    ↓
Sends student_answer + model_answer
    ↓
Backend creates QuestionAnswer objects
    ↓
Send each Q&A pair to Claude API
    ↓
Claude compares student answer with model answer
    ↓
Returns score + feedback
    ↓
Save to Evaluation model
    ↓
Return results to frontend
```

## ⚙️ System Requirements

- Backend running on port 8000
- Frontend running on port 3000
- Claude API key configured in .env
- Python 3.11 with Django, DRF, Anthropic SDK, and PyTorch for SBERT
- Node.js and npm for React

## ✨ Key Features

1. **AI-Powered Question Extraction**: Claude automatically extracts questions from documents
2. **Multi-Format Support**: PDF, DOCX, PPT, XLSX, TXT, Images
3. **User Verification**: Users can review and correct extracted questions
4. **Comprehensive Evaluation**: Claude evaluates answers with detailed feedback
5. **Score Calculation**: Automatic scoring with completeness, accuracy, clarity metrics
6. **Detailed Results**: Strengths, weaknesses, suggestions for improvement
7. **Guest Mode**: Users can test without creating account

## 🐛 Troubleshooting

### File Upload Not Working
- Check backend logs: `/logs/errors.log`
- Ensure file size < 10MB
- Verify backend is running

### Questions Not Extracting
- Check if backend is running
- Verify Claude API key is valid
- Check backend logs for API errors
- Ensure text was extracted from file

### Frontend Not Connecting to Backend
- Verify backend is running on 8000
- Check .env has correct API_URL
- Check browser console for errors
- Verify CORS is enabled in Django

### Evaluation Not Working
- Ensure all questions have both answers filled
- Check Claude API key is valid
- Review backend logs
- Verify exam ID is correct

## 📝 Testing with Sample Data

### Create Test Exam File
```
Question 1: What is photosynthesis?
Student Answer: Plants use sunlight to make food
Expected Answer: Photosynthesis is the process by which plants use sunlight, water, and CO2 to create glucose and oxygen.

Question 2: Explain the water cycle.
Student Answer: Water evaporates and forms clouds
Expected Answer: The water cycle involves evaporation, condensation, precipitation, and collection of water.
```

Save as `.txt` file and upload to test the pipeline.

## 🎯 Next Steps for Production

1. Add CORS configuration if needed
2. Implement rate limiting for API
3. Add authentication tokens expiration handling
4. Implement file cleanup for uploaded documents
5. Add progress tracking for long-running evaluations
6. Create admin panel for monitoring
7. Add email notifications for completed evaluations
8. Implement export to PDF for results
9. Add comparison with previous evaluations
10. Create analytics dashboard

---

**Status**: ✅ All connectivity issues resolved
**Last Updated**: April 6, 2026
**Pipeline Status**: Ready for testing
