import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    passwordConfirm: '',
  });
  const [localError, setLocalError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();
  const { register, loading, error } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!formData.email || !formData.name || !formData.password || !formData.passwordConfirm) {
      setLocalError('Please fill in all fields');
      return false;
    }

    if (formData.password.length < 8) {
      setLocalError('Password must be at least 8 characters long');
      return false;
    }

    if (formData.password !== formData.passwordConfirm) {
      setLocalError('Passwords do not match');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    setSuccess('');

    if (!validateForm()) return;

    try {
      await register(
        formData.email,
        formData.name,
        formData.password,
        formData.passwordConfirm
      );
      setSuccess('Registration successful! Redirecting to dashboard...');
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err) {
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Create Account</h1>
        
        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        {(error || localError) && (
          <div className="error-message">
            {error || localError}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter your full name"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter password (min 8 characters)"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="passwordConfirm">Confirm Password</label>
            <input
              type="password"
              id="passwordConfirm"
              name="passwordConfirm"
              value={formData.passwordConfirm}
              onChange={handleChange}
              placeholder="Confirm password"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
