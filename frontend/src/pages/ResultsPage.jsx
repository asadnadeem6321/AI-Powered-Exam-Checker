import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useEvaluation } from '../context/EvaluationContext';
import Loader from '../components/Loader';
import '../styles/Results.css';

const ResultsPage = () => {
  const { evaluationId } = useParams();
  const { currentEvaluation, loading, error, getEvaluationDetail } = useEvaluation();

  useEffect(() => {
    getEvaluationDetail(evaluationId).catch((err) => {
      console.error('Error loading evaluation:', err);
    });
  }, [evaluationId]);

  if (loading || !currentEvaluation) {
    return <Loader />;
  }

  if (error) {
    return (
      <div className="results-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  const { exam, final_score, grade, overall_feedback, question_evaluations, evaluation_metadata } = currentEvaluation;

  return (
    <div className="results-container">
      <div className="results-header">
        <h1>Evaluation Results</h1>
        <p className="exam-name">{exam.file_name}</p>
      </div>

      <div className="score-card">
        <div className="score-circle">
          <div className="score-value">{final_score.toFixed(1)}</div>
          <div className="score-max">/100</div>
        </div>
        <div className="score-info">
          <h2 className={`grade-${grade}`}>{grade}</h2>
          <p className="score-text">Overall Performance</p>
          <p className="score-formula">Final Score = 0.6 x Similarity + 0.4 x Context</p>
          {evaluation_metadata?.percentage !== undefined && (
            <p className="score-meta">Percentage: {evaluation_metadata.percentage}%</p>
          )}
        </div>
      </div>

      <div className="feedback-section">
        <h2>Overall Feedback</h2>
        <div className="feedback-box">
          <p>{overall_feedback}</p>
        </div>
      </div>

      <div className="questions-section">
        <h2>Question-wise Analysis</h2>
        <div className="questions-list">
          {question_evaluations && question_evaluations.length > 0 ? (
            question_evaluations.map((qEval, index) => (
              <div key={qEval.id} className="question-item">
                <div className="question-header">
                  <h3>Question {index + 1}: {qEval.question.question_text}</h3>
                  <span className={`q-score score-${Math.round(qEval.final_score / 20)}`}>
                    {qEval.final_score.toFixed(1)}/100
                  </span>
                </div>

                <div className="question-content">
                  <div className="qa-pair">
                    <label>Student's Answer:</label>
                    <p className="answer-text">{qEval.question.student_answer}</p>
                  </div>

                  <div className="qa-pair">
                    <label>Model Answer:</label>
                    <p className="answer-text model-answer">{qEval.question.model_answer}</p>
                  </div>
                </div>

                <div className="question-metrics">
                  <div className="metric">
                    <label>Similarity Score (SBERT)</label>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${qEval.similarity_score}%`,
                        }}
                      ></div>
                    </div>
                    <span className="metric-value">{qEval.similarity_score.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Contextual Score (GPT)</label>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${qEval.contextual_score}%`,
                        }}
                      ></div>
                    </div>
                    <span className="metric-value">{qEval.contextual_score.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Completeness</label>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${qEval.completeness}%`,
                        }}
                      ></div>
                    </div>
                    <span className="metric-value">{qEval.completeness?.toFixed(1) || 'N/A'}%</span>
                  </div>

                  <div className="metric">
                    <label>Accuracy</label>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${qEval.accuracy}%`,
                        }}
                      ></div>
                    </div>
                    <span className="metric-value">{qEval.accuracy?.toFixed(1) || 'N/A'}%</span>
                  </div>

                  <div className="metric">
                    <label>Clarity</label>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${qEval.clarity}%`,
                        }}
                      ></div>
                    </div>
                    <span className="metric-value">{qEval.clarity?.toFixed(1) || 'N/A'}%</span>
                  </div>
                </div>

                <div className="question-feedback">
                  <h4>Detailed Feedback</h4>
                  <p>{qEval.feedback}</p>

                  {qEval.strengths && qEval.strengths.length > 0 && (
                    <div className="strengths">
                      <h5>✓ Strengths:</h5>
                      <ul>
                        {qEval.strengths.map((strength, i) => (
                          <li key={i}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {qEval.weaknesses && qEval.weaknesses.length > 0 && (
                    <div className="weaknesses">
                      <h5>✗ Areas for Improvement:</h5>
                      <ul>
                        {qEval.weaknesses.map((weakness, i) => (
                          <li key={i}>{weakness}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {qEval.suggestions && (
                    <div className="suggestions">
                      <h5>💡 Suggestions:</h5>
                      <p>{qEval.suggestions}</p>
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="no-data">No question evaluations available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
