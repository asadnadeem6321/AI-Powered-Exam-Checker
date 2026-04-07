import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useEvaluation } from '../context/EvaluationContext';
import '../styles/Upload.css';

const QuestionFormPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { evaluateExam, loading: ctxLoading, error: ctxError } = useEvaluation();

  const [exam, setExam] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setLocalError] = useState('');
  const [extracting, setExtracting] = useState(true);

  // Extract questions from the uploaded exam
  useEffect(() => {
    const extractQuestionsFromExam = async () => {
      try {
        const examData = location.state?.exam;
        if (!examData) {
          setLocalError('No exam data found');
          setLoading(false);
          return;
        }

        setExam(examData);
        setExtracting(true);

        // Call backend to extract questions
        const response = await fetch(
          `http://localhost:8000/api/exams/${examData.id}/extract-questions/`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`,
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to extract questions');
        }

        const data = await response.json();
        console.log('Extracted questions:', data);

        if (data.data && data.data.questions) {
          setQuestions(data.data.questions);
        } else {
          setLocalError('No questions found in the document');
        }
      } catch (err) {
        console.error('Question extraction error:', err);
        setLocalError(err.message || 'Failed to extract questions from the exam');
      } finally {
        setExtracting(false);
        setLoading(false);
      }
    };

    extractQuestionsFromExam();
  }, [location.state]);

  // Update a question field
  const updateQuestion = (index, field, value) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index][field] = value;
    setQuestions(updatedQuestions);
  };

  // Handle submit to evaluate
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!exam) {
      setLocalError('No exam data available');
      return;
    }

    // Validate all questions have answers
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

      // Prepare questions data for evaluation
      const questionsForEvaluation = questions.map((q) => ({
        question_number: q.question_number,
        question_text: q.question_text,
        student_answer: q.student_answer,
        model_answer: q.model_answer,
      }));

      // Call evaluation endpoint
      const evaluation = await evaluateExam(exam.id, questionsForEvaluation);

      // Navigate to results page
      navigate(`/results/${evaluation.id}`, {
        state: { evaluation, exam },
      });
    } catch (err) {
      console.error('Evaluation error:', err);
      setLocalError(err.message || 'Failed to evaluate exam');
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

  if (extracting) {
    return (
      <div className="upload-container">
        <div className="upload-card">
          <h1>Extracting Questions...</h1>
          <p>AI is analyzing your exam document and extracting questions.</p>
          <p>This may take a moment...</p>
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
          <button
            className="btn btn-primary"
            onClick={() => navigate('/upload')}
          >
            Back to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h1>Review & Complete Exam Questions</h1>
        <p className="upload-subtitle">
          Verify the extracted questions and add expected answers, then click Evaluate
        </p>

        {(error || ctxError) && (
          <div className="error-message">{error || ctxError}</div>
        )}

        {questions.length === 0 ? (
          <div className="error-message">
            No questions could be extracted from the document. Please try uploading a different file.
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="questions-list">
              {questions.map((question, idx) => (
                <div key={idx} className="question-item">
                  <div className="question-header">
                    <h3>Question {question.question_number || idx + 1}</h3>
                    <span className="question-type">{question.question_type || 'essay'}</span>
                  </div>

                  {/* Question Text */}
                  <div className="form-group">
                    <label>Question Text</label>
                    <textarea
                      value={question.question_text || ''}
                      onChange={(e) =>
                        updateQuestion(idx, 'question_text', e.target.value)
                      }
                      placeholder="Question text"
                      rows="3"
                      className="form-control"
                    />
                  </div>

                  {/* Options for MCQ */}
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

                  {/* Student Answer */}
                  <div className="form-group">
                    <label htmlFor={`student-${idx}`}>
                      Student Answer *
                    </label>
                    <textarea
                      id={`student-${idx}`}
                      value={question.student_answer || ''}
                      onChange={(e) =>
                        updateQuestion(idx, 'student_answer', e.target.value)
                      }
                      placeholder="Student's answer (from the exam)"
                      rows="3"
                      className="form-control"
                      required
                    />
                  </div>

                  {/* Model/Expected Answer */}
                  <div className="form-group">
                    <label htmlFor={`model-${idx}`}>
                      Expected Answer (Model Answer) *
                    </label>
                    <textarea
                      id={`model-${idx}`}
                      value={question.model_answer || ''}
                      onChange={(e) =>
                        updateQuestion(idx, 'model_answer', e.target.value)
                      }
                      placeholder="Expected/correct answer (what a perfect answer should contain)"
                      rows="4"
                      className="form-control"
                      required
                    />
                    <small>
                      Enter the complete, ideal answer that the student should have provided.
                    </small>
                  </div>

                  <hr className="question-divider" />
                </div>
              ))}
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-large"
              disabled={ctxLoading || extracting}
            >
              {ctxLoading ? 'Evaluating...' : 'Evaluate & Get Results'}
            </button>
          </form>
        )}

        <button
          className="btn btn-secondary"
          onClick={() => navigate('/upload')}
          style={{ marginTop: '1rem' }}
        >
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
        }

        .question-header h3 {
          margin: 0;
          font-size: 1.1rem;
          color: #333;
        }

        .question-type {
          background-color: #3498db;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 4px;
          font-size: 0.85rem;
          text-transform: capitalize;
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
      `}</style>
    </div>
  );
};

export default QuestionFormPage;
