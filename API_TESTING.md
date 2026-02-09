# API Testing Examples

This file contains example API requests for testing the Exam Checker API.

## Authentication

### 1. Register a New User

```http
POST http://localhost:8000/api/users/register/
Content-Type: application/json

{
    "email": "student@example.com",
    "name": "John Doe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "student@example.com",
        "name": "John Doe",
        "created_at": "2026-02-09T..."
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1...",
        "access": "eyJ0eXAiOiJKV1..."
    }
}
```

### 2. Login

```http
POST http://localhost:8000/api/users/login/
Content-Type: application/json

{
    "email": "student@example.com",
    "password": "SecurePass123!"
}
```

### 3. Get User Profile

```http
GET http://localhost:8000/api/users/profile/
Authorization: Bearer <your_access_token>
```

## Exam Management

### 4. Upload Exam File

```http
POST http://localhost:8000/api/exams/upload/
Authorization: Bearer <your_access_token>
Content-Type: multipart/form-data

file: <select your exam file>
```

**Supported file types:** PDF, TXT, JPG, JPEG, PNG

### 5. List User's Exams

```http
GET http://localhost:8000/api/exams/
Authorization: Bearer <your_access_token>
```

### 6. Get Exam Details

```http
GET http://localhost:8000/api/exams/1/
Authorization: Bearer <your_access_token>
```

## Evaluation

### 7. Evaluate Exam

```http
POST http://localhost:8000/api/evaluations/evaluate/1/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "questions": [
        {
            "question_number": 1,
            "question_text": "What is machine learning?",
            "student_answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make decisions based on data.",
            "model_answer": "Machine learning is a branch of artificial intelligence focused on building systems that learn from data. It involves training algorithms on datasets to make predictions or decisions without explicit programming for each specific task."
        },
        {
            "question_number": 2,
            "question_text": "Explain the difference between supervised and unsupervised learning.",
            "student_answer": "Supervised learning uses labeled data where the algorithm learns from input-output pairs. Unsupervised learning works with unlabeled data to find patterns and structures.",
            "model_answer": "Supervised learning is a type of machine learning where the algorithm is trained on labeled data, with both inputs and desired outputs provided. Unsupervised learning, on the other hand, works with unlabeled data and attempts to discover hidden patterns or structures without predefined outputs."
        }
    ]
}
```

**Response:**
```json
{
    "message": "Evaluation completed successfully",
    "evaluation": {
        "id": 1,
        "exam": {...},
        "similarity_score": 85.5,
        "contextual_score": 88.0,
        "final_score": 86.5,
        "grade": "A",
        "overall_feedback": "Overall performance: EXCELLENT...",
        "question_evaluations": [
            {
                "question": {...},
                "similarity_score": 87.2,
                "contextual_score": 90.0,
                "final_score": 88.3,
                "feedback": "Excellent understanding of machine learning...",
                "strengths": [
                    "Clear explanation",
                    "Good use of examples"
                ],
                "weaknesses": [
                    "Could elaborate more on algorithms"
                ],
                "suggestions": "Consider adding more specific examples...",
                "completeness": 90,
                "accuracy": 92,
                "clarity": 88
            }
        ]
    }
}
```

### 8. Get Evaluation for Specific Exam

```http
GET http://localhost:8000/api/evaluations/exam/1/
Authorization: Bearer <your_access_token>
```

### 9. List All Evaluations

```http
GET http://localhost:8000/api/evaluations/
Authorization: Bearer <your_access_token>
```

## Guest Usage (No Authentication)

### Upload and Evaluate as Guest

```http
POST http://localhost:8000/api/exams/upload/
Content-Type: multipart/form-data

file: <select your exam file>
```

Note: Guest uploads will not be saved to history and will be automatically deleted after evaluation.

## PowerShell Examples

### Register User
```powershell
$body = @{
    email = "test@example.com"
    name = "Test User"
    password = "TestPass123!"
    password_confirm = "TestPass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/users/register/" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
```

### Login
```powershell
$body = @{
    email = "test@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/users/login/" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
$token = $response.tokens.access
Write-Host "Access Token: $token"
```

### Upload File
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

$filePath = "C:\path\to\your\exam.pdf"
$form = @{
    file = Get-Item -Path $filePath
}

Invoke-RestMethod -Uri "http://localhost:8000/api/exams/upload/" -Method Post -Headers $headers -Form $form
```

## Testing with cURL (Git Bash / WSL)

### Register
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### Upload Exam
```bash
curl -X POST http://localhost:8000/api/exams/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/exam.pdf"
```

## Sample Exam Content (for testing)

### Sample Text File (exam_answers.txt)

```
Q1. What is machine learning?
Answer: Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions based on those patterns.

Q2. Explain supervised learning.
Answer: Supervised learning is a type of machine learning where the algorithm learns from labeled training data. Each example in the training set includes both input features and the corresponding correct output, allowing the model to learn the mapping between inputs and outputs.
```

### Model Answers for Evaluation

```json
{
    "questions": [
        {
            "question_number": 1,
            "question_text": "What is machine learning?",
            "model_answer": "Machine learning is a branch of artificial intelligence focused on building systems that can learn from and make decisions based on data. It involves training algorithms on datasets to identify patterns and make predictions without being explicitly programmed for every scenario."
        },
        {
            "question_number": 2,
            "question_text": "Explain supervised learning.",
            "model_answer": "Supervised learning is a machine learning paradigm where algorithms learn from labeled training data. The training dataset contains input-output pairs, and the algorithm learns to map inputs to outputs by finding patterns in the labeled examples."
        }
    ]
}
```

## Expected Evaluation Metrics

- **Similarity Score (SBERT)**: 0-100 (measures semantic similarity)
- **Contextual Score (GPT)**: 0-100 (measures understanding and completeness)
- **Final Score**: Weighted average (60% SBERT + 40% GPT)
- **Grade**: A+, A, A-, B+, B, B-, C+, C, C-, F

## Error Responses

### 400 Bad Request
```json
{
    "error": "File size exceeds maximum limit of 10.00MB",
    "status": "error"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication credentials were not provided.",
    "status": "error"
}
```

### 404 Not Found
```json
{
    "error": "Exam has not been evaluated yet",
    "status": "error"
}
```
