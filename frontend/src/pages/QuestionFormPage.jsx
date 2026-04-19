import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useEvaluation } from '../context/EvaluationContext';
import { examService } from '../services/examService';
import '../styles/Upload.css';

const QuestionFormPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { evaluateExam, loading: ctxLoading, error: ctxError } = useEvaluation();

  const [exam, setExam] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [totalMarks, setTotalMarks] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setLocalError] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [allowManualFallback, setAllowManualFallback] = useState(false);

  useEffect(() => {
    const examData = location.state?.exam;

    if (!examData) {
      setLocalError('No exam data found');
      setLoading(false);
      return;
    }

    setExam(examData);
    if (examData.total_marks) {
      setTotalMarks(String(examData.total_marks));
    }
    setLoading(false);
  }, [location.state]);

  const updateQuestion = (index, field, value) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index][field] = value;
    setQuestions(updatedQuestions);
  };

  const handleExtractQuestions = async () => {
    if (!exam) {
      setLocalError('No exam data available');
      return;
    }

    const parsedMarks = Number(totalMarks);
    if (!Number.isInteger(parsedMarks) || parsedMarks <= 0) {
      setLocalError('Please enter a valid positive integer for total marks');
      return;
    }

    try {
      setExtracting(true);
      setLocalError('');
      setAllowManualFallback(false);

      const response = await examService.extractQuestions(exam.id, parsedMarks);
      const data = response.data;

      if (data.data && Array.isArray(data.data.questions) && data.data.questions.length > 0) {
        setQuestions(data.data.questions);
      } else {
        setLocalError('No questions found in the document');
        setAllowManualFallback(true);
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.error ||
        err?.message ||
        'Failed to extract questions from the exam';

      setLocalError(message);
      setAllowManualFallback(true);
    } finally {
      setExtracting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!exam) {
      setLocalError('No exam data available');
      return;
    }

    if (questions.length === 0) {
      setLocalError('Please extract questions first');
      return;
    }

    const allValid = questions.every(
      (q) => q.student_answer && q.student_answer.trim() && q.model_answer && q.model_answer.trim()
    );

    if (!allValid) {
      setLocalError('Please fill in both student answers and expected answers for all questions');
      return;
    }

    try {
      setExtracting(true);
      setLocalError('');

      const questionsForEvaluation = questions.map((q, index) => ({
        question_number: q.question_number || index + 1,
        question_text: q.question_text,
        student_answer: q.student_answer,
        model_answer: q.model_answer,
        marks: q.marks,
      }));

      const evaluation = await evaluateExam(exam.id, questionsForEvaluation);
      const resultId = evaluation.evaluation_id || evaluation.id || exam.id;

      navigate(`/results/${resultId}`, {
        state: { evaluation, exam },
      });
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.error ||
        err?.message ||
        'Failed to evaluate exam';
      setLocalError(message);
    } finally {
      setExtracting(false);
    }
  };

  if (loading) {
    return (
      <div className="upload-container">
        <div className="upload-card">
          <h1>Loading Exam Data...</h1>
          <p>Please wait while we prepare your exam.</p>
        </div>
      </div>
    );
  }

  if (error || ctxError) {
    return (
      <div className="upload-container">
        <div className="upload-card">
          <h1>Error</h1>
          <div className="error-message">{error || ctxError}</div>
          <button className="btn btn-primary" onClick={() => navigate('/upload')}>
            Back to Upload
          </button>
          {allowManualFallback && (
            <button
              className="btn btn-secondary"
              style={{ marginLeft: '0.75rem' }}
              onClick={() => navigate('/manual-entry', { state: { examId: exam?.id || null } })}
            >
              Enter Questions Manually
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h1>Review And Complete Exam Questions</h1>
        <p className="upload-subtitle">
          Enter total marks, extract questions, then evaluate with marks-aware scoring
        </p>

        {(error || ctxError) && <div className="error-message">{error || ctxError}</div>}

        {questions.length === 0 ? (
          <div className="marks-setup-card">
            <div className="form-group">
              <label htmlFor="total-marks">Total Exam Marks *</label>
              <input
                id="total-marks"
                type="number"
                min="1"
                value={totalMarks}
                onChange={(e) => setTotalMarks(e.target.value)}
                className="form-control"
                placeholder="e.g. 100"
              />
              <small>This is required to allocate marks across extracted questions.</small>
            </div>

            <button
              type="button"
              className="btn btn-primary btn-large"
              onClick={handleExtractQuestions}
              disabled={extracting}
            >
              {extracting ? 'Extracting Questions...' : 'Extract Questions'}
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="questions-list">
              {questions.map((question, idx) => (
                <div key={idx} className="question-item">
                  <div className="question-header">
                    <h3>Question {question.question_number || idx + 1}</h3>
                    <div className="question-meta">
                      <span className="question-type">{question.question_type || 'essay'}</span>
                      <span className="question-marks">{question.marks ?? 0} marks</span>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Question Text</label>
                    <textarea
                      value={question.question_text || ''}
                      onChange={(e) => updateQuestion(idx, 'question_text', e.target.value)}
                      placeholder="Question text"
                      rows="3"
                      className="form-control"
                    />
                  </div>

                  {question.question_type === 'multiple_choice' && question.options && (
                    <div className="form-group">
                      <label>Options</label>
                      <div className="options-list">
                        {question.options.map((option, optIdx) => (
                          <p key={optIdx} className="option-text">
                            {option}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="form-group">
                    <label htmlFor={`student-${idx}`}>Student Answer *</label>
                    <textarea
                      id={`student-${idx}`}
                      value={question.student_answer || ''}
                      onChange={(e) => updateQuestion(idx, 'student_answer', e.target.value)}
                      placeholder="Student's answer (from the exam)"
                      rows="3"
                      className="form-control"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor={`model-${idx}`}>Expected Answer (Model Answer) *</label>
                    <textarea
                      id={`model-${idx}`}
                      value={question.model_answer || ''}
                      onChange={(e) => updateQuestion(idx, 'model_answer', e.target.value)}
                      placeholder="Expected/correct answer"
                      rows="4"
                      className="form-control"
                      required
                    />
                  </div>

                  <hr className="question-divider" />
                </div>
              ))}
            </div>

            <button type="submit" className="btn btn-primary btn-large" disabled={ctxLoading || extracting}>
              {ctxLoading || extracting ? 'Evaluating...' : 'Evaluate And Get Results'}
            </button>
          </form>
        )}

        <button className="btn btn-secondary" onClick={() => navigate('/upload')} style={{ marginTop: '1rem' }}>
          Back to Upload
        </button>
      </div>

      <style jsx>{`
        .questions-list {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          margin: 1.5rem 0;
        }

        .marks-setup-card {
          background: #f8fbff;
          border: 1px solid #d9e9ff;
          border-radius: 8px;
          padding: 1rem;
          margin: 1rem 0;
        }

        .question-item {
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 1rem;
          background-color: #fafafa;
        }

        .question-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          gap: 1rem;
        }

        .question-header h3 {
          margin: 0;
          font-size: 1.1rem;
          color: #333;
        }

        .question-meta {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .question-type {
          background-color: #3498db;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          font-size: 0.85rem;
          text-transform: capitalize;
        }

        .question-marks {
          background-color: #2ecc71;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #333;
        }

        .form-control {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-family: Arial, sans-serif;
          font-size: 1rem;
          resize: vertical;
        }

        .form-control:focus {
          outline: none;
          border-color: #3498db;
          box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
        }

        .form-group small {
          display: block;
          margin-top: 0.25rem;
          color: #666;
          font-size: 0.9rem;
        }

        .options-list {
          background-color: #f5f5f5;
          border-left: 3px solid #3498db;
          padding: 0.75rem;
          border-radius: 4px;
        }

        .option-text {
          margin: 0.5rem 0;
          color: #333;
          font-size: 0.95rem;
        }

        .question-divider {
          border: none;
          border-top: 1px dashed #ddd;
          margin: 1.5rem 0 0 0;
        }

        .btn-secondary {
          background-color: #95a5a6;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1rem;
          transition: background-color 0.3s;
        }

        .btn-secondary:hover:not(:disabled) {
          background-color: #7f8c8d;
        }

        .error-message {
          background-color: #fee;
          border: 1px solid #fcc;
          color: #c33;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1rem;
        }

        @media (max-width: 768px) {
          .question-header {
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default QuestionFormPage;
