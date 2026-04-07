import api from './api';

// User Authentication Services
export const userService = {
  register: (email, name, password, passwordConfirm) =>
    api.post('/users/register/', {
      email,
      name,
      password,
      password_confirm: passwordConfirm,
    }),

  login: (email, password) =>
    api.post('/users/login/', { email, password }),

  logout: (refreshToken) =>
    api.post('/users/logout/', { refresh_token: refreshToken }),

  getProfile: () =>
    api.get('/users/profile/'),

  refreshToken: (refreshToken) =>
    api.post('/users/token/refresh/', { refresh: refreshToken }),
};

// Exam Services
export const examService = {
  uploadExam: (file) => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post('/exams/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getExams: () =>
    api.get('/exams/'),

  getExamDetail: (examId) =>
    api.get(`/exams/${examId}/`),

  deleteExam: (examId) =>
    api.delete(`/exams/${examId}/delete/`),

  extractQuestions: (examId) =>
    api.post(`/exams/${examId}/extract-questions/`),
};

// Evaluation Services
export const evaluationService = {
  evaluateExam: (examId, questions) =>
    api.post(`/evaluations/evaluate/${examId}/`, { questions }),

  getEvaluations: () =>
    api.get('/evaluations/'),

  getEvaluationDetail: (evaluationId) =>
    api.get(`/evaluations/${evaluationId}/`),

  getExamEvaluation: (examId) =>
    api.get(`/evaluations/exam/${examId}/`),
};
