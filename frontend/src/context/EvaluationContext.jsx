import React, { createContext, useState, useContext, useCallback } from 'react';
import { examService, evaluationService } from '../services/examService';

const EvaluationContext = createContext();

export const useEvaluation = () => {
  const context = useContext(EvaluationContext);
  if (!context) {
    throw new Error('useEvaluation must be used within EvaluationProvider');
  }
  return context;
};

export const EvaluationProvider = ({ children }) => {
  const [exams, setExams] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [currentExam, setCurrentExam] = useState(null);
  const [currentEvaluation, setCurrentEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const uploadExam = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    try {
      const response = await examService.uploadExam(file);
      const exam = response.data.exam;
      setCurrentExam(exam);
      return exam;
    } catch (err) {
      console.error('Upload error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message,
        isAxiosError: err.isAxiosError,
      });
      
      let errorMessage = 'Upload failed';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getExams = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await examService.getExams();
      setExams(response.data || []);
      return response.data || [];
    } catch (err) {
      setError('Failed to fetch exams');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const evaluateExam = useCallback(async (examId, questions) => {
    setLoading(true);
    setError(null);
    try {
      const response = await evaluationService.evaluateExam(examId, questions);
      const evaluation = response.data.evaluation;
      setCurrentEvaluation(evaluation);
      return evaluation;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Evaluation failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getEvaluations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await evaluationService.getEvaluations();
      setEvaluations(response.data || []);
      return response.data || [];
    } catch (err) {
      setError('Failed to fetch evaluations');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getEvaluationDetail = useCallback(async (evaluationId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await evaluationService.getEvaluationDetail(evaluationId);
      setCurrentEvaluation(response.data);
      return response.data;
    } catch (err) {
      setError('Failed to fetch evaluation');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteExam = useCallback(async (examId) => {
    setLoading(true);
    setError(null);
    try {
      await examService.deleteExam(examId);
      setExams((prevExams) => prevExams.filter((e) => e.id !== examId));
      return true;
    } catch (err) {
      setError('Failed to delete exam');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const value = {
    exams,
    evaluations,
    currentExam,
    currentEvaluation,
    loading,
    error,
    uploadExam,
    getExams,
    evaluateExam,
    getEvaluations,
    getEvaluationDetail,
    deleteExam,
    setError,
  };

  return (
    <EvaluationContext.Provider value={value}>{children}</EvaluationContext.Provider>
  );
};
