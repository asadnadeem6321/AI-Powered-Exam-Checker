import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../services/examService';
import '../styles/Auth.css';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);

    try {
      const res = await userService.passwordResetRequest(email);
      setMessage(res.data.message || 'If an account exists, a reset email was sent.');
    } catch (err) {
      console.error('Password reset request failed', err);
      setMessage('Failed to send reset email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Forgot Password</h1>
        {message && <div className="info-message">{message}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <p className="auth-link">
          Remembered? <a href="/login">Login</a>
        </p>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
