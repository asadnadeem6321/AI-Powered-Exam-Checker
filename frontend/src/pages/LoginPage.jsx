import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState('');

  const navigate = useNavigate();
  const { login, loading, error, isAuthenticated } = useAuth();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');

    if (!email || !password) {
      setLocalError('Please fill in all fields');
      return;
    }

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
    }
  };

  const handleGuestAccess = () => {
    navigate('/upload');
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Login</h1>
        
        {(error || localError) && (
          <div className="error-message">
            {error || localError}
          </div>
        )}

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

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Login'}
          </button>
        </form>

        <div className="divider">OR</div>

        <button
          className="btn btn-secondary"
          onClick={handleGuestAccess}
          disabled={loading}
        >
          Continue as Guest
        </button>

        <p className="auth-link">
          Don't have an account? <Link to="/register">Register here</Link>
        </p>

        <p className="auth-link">
          <Link to="/forgot-password">Forgot password?</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
