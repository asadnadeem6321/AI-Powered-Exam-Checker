import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEvaluation } from '../context/EvaluationContext';
import { evaluationService } from '../services/examService';
import Loader from '../components/Loader';
import '../styles/Dashboard.css';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { exams, evaluations, loading, error, getExams, getEvaluations, deleteExam } = useEvaluation();
  const [activeTab, setActiveTab] = useState('exams');
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        await getExams();
        await getEvaluations();
      } catch (err) {
        console.error('Error loading data:', err);
      }
    };
    loadData();
  }, [getExams, getEvaluations]);

  const handleDelete = async (examId) => {
    try {
      await deleteExam(examId);
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Error deleting exam:', err);
    }
  };

  const handleViewResult = (evaluationId) => {
    navigate(`/results/${evaluationId}`);
  };

  const handleViewResultByExam = async (examId) => {
    try {
      const response = await evaluationService.getExamEvaluation(examId);
      const evaluationId = response?.data?.evaluation?.id;
      if (evaluationId) {
        navigate(`/results/${evaluationId}`);
      } else {
        console.error('Evaluation id missing in exam-evaluation response');
      }
    } catch (err) {
      console.error('Error fetching evaluation by exam:', err);
    }
  };

  if (loading && exams.length === 0) {
    return <Loader />;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button
          onClick={() => navigate('/upload')}
          className="btn btn-primary"
        >
          Upload New Exam
        </button>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'exams' ? 'active' : ''}`}
          onClick={() => setActiveTab('exams')}
        >
          Recent Exams ({exams.length})
        </button>
        <button
          className={`tab ${activeTab === 'evaluations' ? 'active' : ''}`}
          onClick={() => setActiveTab('evaluations')}
        >
          Evaluations ({evaluations.length})
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'exams' && (
          <div className="exams-list">
            {exams.length === 0 ? (
              <p className="empty-state">No exams uploaded yet</p>
            ) : (
              <div className="items-grid">
                {exams.map((exam) => (
                  <div key={exam.id} className="exam-card">
                    <div className="exam-header">
                      <h3>{exam.file_name}</h3>
                      <span className={`status status-${exam.status}`}>
                        {exam.status}
                      </span>
                    </div>
                    <div className="exam-details">
                      <p><strong>Type:</strong> {exam.file_type}</p>
                      <p><strong>Size:</strong> {(exam.file_size / 1024).toFixed(2)} KB</p>
                      <p><strong>Uploaded:</strong> {new Date(exam.uploaded_at).toLocaleDateString()}</p>
                    </div>
                    <div className="exam-actions">
                      {exam.has_evaluation && (
                        <button
                          onClick={() => handleViewResultByExam(exam.id)}
                          className="btn btn-small btn-primary"
                        >
                          View Result
                        </button>
                      )}
                      {deleteConfirm === exam.id ? (
                        <div className="confirm-delete">
                          <p>Delete this exam?</p>
                          <button
                            onClick={() => handleDelete(exam.id)}
                            className="btn btn-small btn-danger"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="btn btn-small"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(exam.id)}
                          className="btn btn-small btn-danger"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'evaluations' && (
          <div className="evaluations-list">
            {evaluations.length === 0 ? (
              <p className="empty-state">No evaluations yet</p>
            ) : (
              <div className="items-grid">
                {evaluations.map((evaluation) => (
                  <div key={evaluation.id} className="evaluation-card">
                    <div className="eval-header">
                      <h3>{evaluation.exam_file_name}</h3>
                      <span className={`grade grade-${evaluation.grade}`}>
                        {evaluation.grade}
                      </span>
                    </div>
                    <div className="eval-details">
                      <div className="score">
                        <span className="score-value">{evaluation.final_score.toFixed(1)}</span>
                        <span className="score-label">/100</span>
                      </div>
                      <p><strong>Evaluated:</strong> {new Date(evaluation.created_at).toLocaleDateString()}</p>
                    </div>
                    <button
                      onClick={() => handleViewResult(evaluation.id)}
                      className="btn btn-primary btn-full"
                    >
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
