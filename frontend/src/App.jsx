import React from 'react';
import './styles/index.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { EvaluationProvider } from './context/EvaluationContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import QuestionFormPage from './pages/QuestionFormPage';
import ManualEntryPage from './pages/ManualEntryPage';
import ResultsPage from './pages/ResultsPage';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <EvaluationProvider>
          <div className="App">
            <Navbar />
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LoginPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/question-form" element={<QuestionFormPage />} />
              <Route path="/manual-entry" element={<ManualEntryPage />} />
              
              {/* Protected Routes */}
              <Route 
                path="/dashboard" 
                element={<PrivateRoute component={DashboardPage} />} 
              />
              <Route path="/results/:evaluationId" element={<ResultsPage />} />
              
              {/* Catch all */}
              <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
          </div>
        </EvaluationProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
