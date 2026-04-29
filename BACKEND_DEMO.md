Backend Demonstration Guide

Purpose
- Capture and demonstrate backend services for the AI-Powered Exam Checker.
- Include logs, API request/response examples, DB snapshots and exact commands so you can take screenshots for your supervisor.

What I captured (files & locations)
- Server error log: logs/errors.log
- Database: db.sqlite3 (SQLite) in project root
- Uploaded files: media/exams/*
- Relevant handlers: `exams/views.py`, `exam_checker/ai_engine/text_extractor.py`, `exam_checker/ai_engine/ocr_handler.py`, `evaluations/views.py`

High-level pipeline (what to show)
1. Upload file (POST `/api/exams/upload/`) — file arrives in `media/` and `Exam` record created.
2. Text extraction — `TextExtractor` calls `OCRHandler` (Tesseract) or PDF text extraction; `Exam.raw_text` stored.
3. Extract questions — POST `/api/exams/{exam_id}/extract-questions/` uses `QuestionExtractor` (Claude API) then segmentation and writes `QuestionAnswer` rows.
4. Evaluate — POST `/api/evaluations/evaluate/{exam_id}/` runs `HybridEvaluator`/`EnhancedHybridEvaluator`, persists `Evaluation` and `QuestionEvaluation` rows.
5. Results retrieval — GET `/api/evaluations/exam/{exam_id}/` and GET `/api/exams/{exam_id}/` to show stored raw_text, questions and evaluation.

Important log excerpts (captured from `logs/errors.log`)
- Host header errors when binding to 0.0.0.0:/ALLOWED_HOSTS:

```
Invalid HTTP_HOST header: '0.0.0.0:8000'. You may need to add '0.0.0.0' to ALLOWED_HOSTS.
```

- Tesseract not found (OCR will fail if system Tesseract not installed):

```
Error extracting text from image: /usr/local/bin/tesseract is not installed or it's not in your PATH.
```

- Claude API model-not-found errors (question extraction failures):

```
Error extracting questions (attempt 1): Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-3-5-sonnet-20241022'}}
```

- Missing dependency for JWT used by SimpleJWT (registration/login failures):

```
Unhandled exception: No module named 'jwt'
ModuleNotFoundError: No module named 'jwt'
```

Where to take screenshots (exact targets)
- Terminal showing the Django server process and the command used to start it (timestamp). Command example:

```bash
# Show running Python process on port 8000
lsof -iTCP:8000 -sTCP:LISTEN -n -P
```

- Tail the error log while reproducing an upload to capture real-time messages:

```bash
tail -n 200 logs/errors.log
# or live
tail -f logs/errors.log
```

- The POST response to `/api/exams/upload/` (use curl or Postman). Example command:

```bash
curl -i -X POST http://localhost:8000/api/exams/upload/ \
  -H "Accept: application/json" \
  -F "file=@/absolute/path/to/sample_exam.pdf"
```

- The `media/` directory listing showing the uploaded file path:

```bash
ls -la media/exams/ | tail -n 20
```

- GET exam detail to show `raw_text` and `status`:

```bash
curl -s http://localhost:8000/api/exams/1/ | jq .
```

- POST extract-questions and show returned `questions` payload:

```bash
curl -s -X POST http://localhost:8000/api/exams/1/extract-questions/ \
  -H "Content-Type: application/json" \
  -d '{"total_marks": 100}' | jq .
```

- POST evaluate and show the evaluation response (per-question scores):

```bash
curl -s -X POST http://localhost:8000/api/evaluations/evaluate/1/ \
  -H "Content-Type: application/json" \
  -d @questions_payload.json | jq .
```

- SQLite DB snapshot commands (show rows you can screenshot):

```bash
sqlite3 db.sqlite3 "select id, file_name, raw_text IS NOT NULL, status from exams_exam order by id desc limit 5;"
sqlite3 db.sqlite3 "select id, question_number, marks, student_answer, model_answer from exams_questionanswer where exam_id=1;"
sqlite3 db.sqlite3 "select id, final_score, similarity_score, contextual_score from evaluations_evaluation where exam_id=1;"
```

Suggested screenshot checklist (order to present to supervisor)
- Terminal showing server up + PID and port
- `tail -f logs/errors.log` showing OCR/AI/jwt errors (or success lines if you repeat run)
- `curl` upload request and HTTP response body (success or error)
- `ls media/exams/` showing the saved file
- GET `/api/exams/{id}/` showing `raw_text` and processed timestamps
- POST `/api/exams/{id}/extract-questions/` response showing `questions`
- POST `/api/evaluations/evaluate/{id}/` response showing per-question scores
- SQLite query outputs for `exams_exam`, `exams_questionanswer`, `evaluations_evaluation`

Notes, common fixes and prerequisites
- Tesseract must be installed on the host (macOS common paths):
  - Intel: `/usr/local/bin/tesseract`
  - Apple Silicon: `/opt/homebrew/bin/tesseract`
  - Install via Homebrew: `brew install tesseract`
- Add `0.0.0.0` or the host used to `ALLOWED_HOSTS` in `exam_checker/settings.py` during demo if you run server as `0.0.0.0`.
- Install missing Python deps seen in logs:

```bash
pip install PyJWT torch sentence-transformers pytesseract opencv-python-headless
```

(only install `torch` if you need SBERT; it can be heavy on CPU)

What I can deliver next
- A prepared PDF/Markdown slide (I will produce `BACKEND_DEMO.md` in this repo — you can attach screenshots in-place), already created in the repo root.
- If you want, I can run the full flow here (upload → extract → extract-questions → evaluate) and capture the API responses and DB outputs into files in `demo_artifacts/` so you can screenshot them directly. Confirm and I will proceed.

Files I created
- `BACKEND_DEMO.md` (this document)

----

If you want me to proceed and run the full end-to-end flow and save artifacts for screenshots, reply "Proceed: run end-to-end" and I will run the upload + extract + evaluate using an existing sample file in `media/exams/guest/` and save the responses and DB snapshots under `demo_artifacts/` for you to screenshot.
