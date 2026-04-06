# Backend Testing Guide

## Setup Test Environment

### Install Testing Dependencies
```bash
pip install pytest pytest-django pytest-cov
```

### Configure pytest (pytest.ini)
```ini
[pytest]
DJANGO_SETTINGS_MODULE = exam_checker.settings
python_files = tests.py test_*.py *_tests.py
testpaths = tests
```

## Running Tests

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Class
```bash
python manage.py test tests.test_users.UserRegistrationTestCase
```

### Run Specific Test Method
```bash
python manage.py test tests.test_users.UserRegistrationTestCase.test_user_registration_success
```

### Run with pytest
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=. --cov-report=html
```

## Test Files Location

```
tests/
├── __init__.py
├── test_users.py           # User authentication tests
├── test_exams.py           # Exam management tests
├── test_evaluations.py     # Evaluation tests
└── test_ai_engine.py       # AI engine tests
```

## Test Coverage

### User Authentication Tests
- ✅ User registration (valid/invalid data)
- ✅ User login (valid/invalid credentials)
- ✅ User profile retrieval
- ✅ Token refresh
- ✅ User logout

### Exam Management Tests
- ✅ File upload (valid/invalid files)
- ✅ File size validation
- ✅ File type validation
- ✅ Guest user uploads
- ✅ Exam listing
- ✅ Exam deletion

### Evaluation Tests
- ✅ Single question evaluation
- ✅ Multiple question evaluation
- ✅ Grade calculation
- ✅ Evaluation retrieval
- ✅ Evaluation listing

### AI Engine Tests
- ✅ SBERT similarity computation
- ✅ Text preprocessing
- ✅ Question segmentation
- ✅ Hybrid score calculation

## Frontend Test Files Location

```
frontend/src/__tests__/
├── App.test.js             # Component integration tests
├── LoginPage.test.js       # Login component tests
├── UploadPage.test.js      # Upload component tests
├── DashboardPage.test.js   # Dashboard tests
├── ResultsPage.test.js     # Results display tests
└── AuthContext.test.js     # Authentication context tests
```

## Running Frontend Tests

### Run All Frontend Tests
```bash
cd frontend
npm test
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

### Run Specific Test Suite
```bash
npm test -- LoginPage
```

### Watch Mode (Auto-rerun on file changes)
```bash
npm test -- --watch
```

## Test Best Practices

### Backend Tests
1. **Isolation**: Each test should be independent
2. **Setup/Teardown**: Use setUp() and tearDown() methods
3. **Mocking**: Mock external dependencies (API calls, DB)
4. **Assertions**: Use clear, specific assertions
5. **Documentation**: Add docstrings explaining test purpose

### Frontend Tests
1. **Component Rendering**: Test components render correctly
2. **User Interactions**: Test clicking, typing, submitting
3. **State Management**: Test context providers work correctly
4. **API Integration**: Mock API calls with jest.mock()
5. **Accessibility**: Test keyboard navigation and screen readers

## Coverage Goals

- **Backend**: Aim for 80%+ code coverage
- **Frontend**: Aim for 70%+ code coverage
- **Critical Paths**: 100% coverage for auth, evaluation, uploads

## CI/CD Integration

### For GitHub Actions (`.github/workflows/tests.yml`)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python manage.py test

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: cd frontend && npm ci
      - run: npm test -- --coverage
```

## Common Issues and Solutions

### Issue: Tests fail with database errors
```bash
# Solution: Run migrations before tests
python manage.py migrate --settings=exam_checker.settings_test
```

### Issue: Import errors in tests
```bash
# Solution: Ensure tests directory has __init__.py
touch tests/__init__.py
```

### Issue: Frontend tests not finding components
```bash
# Solution: Check module paths in import statements
```

### Issue: API mocking not working
```bash
# Solution: Mock before importing component
jest.mock('../services/examService');
```

## Performance Testing

### Load Testing SBERT
```python
import time
from exam_checker.ai_engine.sbert_handler import SBERTHandler

sbert = SBERTHandler()
start = time.time()
for i in range(100):
    sbert.compute_similarity("text1", "text2")
print(f"Time for 100 comparisons: {time.time() - start}s")
```

## Test Reporting

### Generate Coverage Report
```bash
pytest --cov=. --cov-report=html --cov-report=term
# Open htmlcov/index.html in browser
```

### View TestResults
```bash
python manage.py test --verbosity=2
```

## Continuous Improvement

- Run tests before every commit
- Maintain test coverage above 75%
- Review failing tests immediately
- Update tests when requirements change
- Document complex test scenarios
