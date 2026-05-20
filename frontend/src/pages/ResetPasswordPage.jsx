import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { userService } from '../services/examService';
import '../styles/Auth.css';

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [uid, setUid] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const u = searchParams.get('uid') || '';
    const t = searchParams.get('token') || '';
    setUid(u);
    setToken(t);
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);

    try {
      const res = await userService.passwordResetConfirm(uid, token, newPassword);
      setMessage(res.data.message || 'Password reset successful');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      console.error('Password reset confirm failed', err);
      setMessage(err?.response?.data?.error || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Reset Password</h1>
        {message && <div className="info-message">{message}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new password"
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Reset Password'}
          </button>
        </form>

        <p className="auth-link">
          Back to <a href="/login">Login</a>
        </p>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
