import React, { useEffect, useMemo } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useEvaluation } from '../context/EvaluationContext';
import Loader from '../components/Loader';
import '../styles/Results.css';

const asNumber = (value, fallback = 0) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
};

const sanitizeFeedback = (text) => {
  if (!text || typeof text !== 'string') return text || '';
  const idx = text.search(/RECOMMENDATIONS?:/i);
  if (idx === -1) return text.trim();
  return text.slice(0, idx).trim();
};

const normalizeMarksPayload = (evaluation, fallbackExamName = '') => {
  const percentage = asNumber(evaluation?.percentage, 0);
  const questionResults = Array.isArray(evaluation?.question_results)
    ? evaluation.question_results
    : [];

  return {
    examName: fallbackExamName,
    finalScore: percentage,
    grade: evaluation?.grade || 'N/A',
    feedback: sanitizeFeedback(evaluation?.feedback || 'No feedback available.'),
    totalAllocatedMarks: asNumber(evaluation?.total_allocated_marks, 0),
    totalObtainedMarks: asNumber(evaluation?.total_obtained_marks, 0),
    totalQuestions: asNumber(evaluation?.total_questions, questionResults.length),
    questionItems: questionResults.map((qEval, index) => ({
      id: `${qEval.question_number || index + 1}-${index}`,
      questionNumber: qEval.question_number || index + 1,
      questionText: qEval.question_text || 'Question text unavailable',
      studentAnswer: qEval.student_answer || '',
      modelAnswer: qEval.model_answer || '',
      similarityScore: asNumber(qEval.similarity_score, 0),
      contextualScore: asNumber(qEval.contextual_score, 0),
      keywordScore: asNumber(qEval.keyword_score, 0),
      lengthScore: asNumber(qEval.length_score, qEval.length_adequacy),
      structureScore: asNumber(qEval.structure_score, 0),
      completeness: asNumber(qEval.completeness, 0),
      accuracy: asNumber(qEval.accuracy, 0),
      clarity: asNumber(qEval.clarity, 0),
      finalScore: asNumber(qEval.final_score_pct, 0),
      marksAllocated: asNumber(qEval.marks_allocated, 0),
      obtainedMarks: asNumber(qEval.obtained_marks, 0),
      feedback: qEval.feedback || '',
      strengths: Array.isArray(qEval.strengths) ? qEval.strengths : [],
      weaknesses: Array.isArray(qEval.weaknesses) ? qEval.weaknesses : [],
    })),
  };
};

const normalizeStoredPayload = (evaluation) => {
  const metadata = evaluation?.evaluation_metadata || {};
  const questionEvals = Array.isArray(evaluation?.question_evaluations)
    ? evaluation.question_evaluations
    : [];

  return {
    examName: evaluation?.exam?.file_name || 'Exam',
    finalScore: asNumber(evaluation?.final_score, 0),
    grade: evaluation?.grade || 'N/A',
    feedback: sanitizeFeedback(evaluation?.overall_feedback || 'No feedback available.'),
    totalAllocatedMarks: asNumber(metadata?.total_allocated_marks, 0),
    totalObtainedMarks: asNumber(metadata?.total_obtained_marks, 0),
    totalQuestions: asNumber(metadata?.total_questions, questionEvals.length),
    questionItems: questionEvals.map((qEval, index) => ({
      id: qEval.id || `${index}`,
      questionNumber: qEval?.question?.question_number || index + 1,
      questionText: qEval?.question?.question_text || 'Question text unavailable',
      studentAnswer: qEval?.question?.student_answer || '',
      modelAnswer: qEval?.question?.model_answer || '',
      similarityScore: asNumber(qEval.similarity_score, 0),
      contextualScore: asNumber(qEval.contextual_score, 0),
      keywordScore: asNumber(qEval.keyword_score || metadata?.question_results?.[index]?.keyword_score, 0),
      lengthScore: asNumber(qEval.length_score || metadata?.question_results?.[index]?.length_score || metadata?.question_results?.[index]?.length_adequacy, 0),
      structureScore: asNumber(qEval.structure_score || metadata?.question_results?.[index]?.structure_score, 0),
      completeness: asNumber(qEval.completeness, 0),
      accuracy: asNumber(qEval.accuracy, 0),
      clarity: asNumber(qEval.clarity, 0),
      finalScore: asNumber(qEval.final_score, 0),
      marksAllocated: asNumber(qEval?.question?.marks, 0),
      obtainedMarks: asNumber(qEval?.question?.obtained_marks, 0),
      feedback: qEval.feedback || '',
      strengths: Array.isArray(qEval.strengths) ? qEval.strengths : [],
      weaknesses: Array.isArray(qEval.weaknesses) ? qEval.weaknesses : [],
    })),
  };
};

const ResultsPage = () => {
  const { evaluationId } = useParams();
  const location = useLocation();
  const { currentEvaluation, loading, error, getEvaluationDetail } = useEvaluation();

  const inlineEvaluation = location.state?.evaluation || null;
  const inlineExamName = location.state?.exam?.file_name || '';

  useEffect(() => {
    if (inlineEvaluation) {
      return;
    }

    const numericId = Number(evaluationId);
    if (Number.isFinite(numericId)) {
      getEvaluationDetail(evaluationId).catch((err) => {
        console.error('Error loading evaluation:', err);
      });
    }
  }, [evaluationId, getEvaluationDetail, inlineEvaluation]);

  const normalized = useMemo(() => {
    if (inlineEvaluation && inlineEvaluation.total_questions !== undefined) {
      return normalizeMarksPayload(inlineEvaluation, inlineExamName);
    }

    if (currentEvaluation) {
      return normalizeStoredPayload(currentEvaluation);
    }

    return null;
  }, [inlineEvaluation, inlineExamName, currentEvaluation]);

  if ((loading && !normalized) || (!normalized && !error)) {
    return <Loader />;
  }

  if (error && !normalized) {
    return (
      <div className="results-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!normalized) {
    return (
      <div className="results-container">
        <div className="error-message">No evaluation data available.</div>
      </div>
    );
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <h1>Evaluation Results</h1>
        <p className="exam-name">{normalized.examName}</p>
      </div>

      <div className="score-card">
        <div className="score-circle">
          <div className="score-value">{normalized.finalScore.toFixed(1)}</div>
          <div className="score-max">/100</div>
        </div>
        <div className="score-info">
          <h2 className={`grade-${normalized.grade}`}>{normalized.grade}</h2>
          <p className="score-text">Overall Performance</p>
          <p className="score-formula">Final Score = 0.7 x Similarity + 0.3 x Context</p>
          <p className="score-meta">Questions: {normalized.totalQuestions}</p>
          <p className="score-meta">
            Marks: {normalized.totalObtainedMarks.toFixed(2)} / {normalized.totalAllocatedMarks}
          </p>
        </div>
      </div>

      <div className="feedback-section">
        <h2>Overall Feedback</h2>
        <div className="feedback-box">
          <p>{normalized.feedback}</p>
        </div>
      </div>

      <div className="questions-section">
        <h2>Question-wise Analysis</h2>
        <div className="questions-list">
          {normalized.questionItems.length > 0 ? (
            normalized.questionItems.map((qEval) => (
              <div key={qEval.id} className="question-item">
                <div className="question-header">
                  <h3>
                    Question {qEval.questionNumber}: {qEval.questionText}
                  </h3>
                  <div className="question-header-right">
                    <span className={`q-score score-${Math.max(1, Math.min(5, Math.round(qEval.finalScore / 20)))}`}>
                      {qEval.finalScore.toFixed(1)}/100
                    </span>
                    <span className="q-marks">
                      {qEval.obtainedMarks.toFixed(2)} / {qEval.marksAllocated} marks
                    </span>
                  </div>
                </div>

                <div className="question-content">
                  <div className="qa-pair">
                    <label>Student's Answer:</label>
                    <p className="answer-text">{qEval.studentAnswer}</p>
                  </div>

                  <div className="qa-pair">
                    <label>Model Answer:</label>
                    <p className="answer-text model-answer">{qEval.modelAnswer}</p>
                  </div>
                </div>

                <div className="question-metrics">
                  <div className="metric">
                    <label>Similarity Score (SBERT)</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.similarityScore}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.similarityScore.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Keyword Coverage</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.keywordScore}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.keywordScore.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Length Adequacy</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.lengthScore}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.lengthScore.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Structure Score</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.structureScore}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.structureScore.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Completeness</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.completeness}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.completeness.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Accuracy</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.accuracy}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.accuracy.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Clarity</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${qEval.clarity}%` }}></div>
                    </div>
                    <span className="metric-value">{qEval.clarity.toFixed(1)}%</span>
                  </div>
                </div>

                <div className="question-feedback">
                  <h4>Detailed Feedback</h4>
                  <p>{qEval.feedback}</p>

                  {qEval.strengths.length > 0 && (
                    <div className="strengths">
                      <h5>Strengths:</h5>
                      <ul>
                        {qEval.strengths.map((strength, i) => (
                          <li key={i}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {qEval.weaknesses.length > 0 && (
                    <div className="weaknesses">
                      <h5>Areas for Improvement:</h5>
                      <ul>
                        {qEval.weaknesses.map((weakness, i) => (
                          <li key={i}>{weakness}</li>
                        ))}
                      </ul>
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
