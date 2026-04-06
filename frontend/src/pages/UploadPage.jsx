import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEvaluation } from '../context/EvaluationContext';
import '../styles/Upload.css';

const UploadPage = () => {
  const navigate = useNavigate();
  const { uploadExam, loading, error } = useEvaluation();
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [localError, setLocalError] = useState('');

  const ALLOWED_TYPES = ['application/pdf', 'text/plain', 'image/jpeg', 'image/png'];
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB

  const validateFile = (selectedFile) => {
    if (!selectedFile) {
      setLocalError('Please select a file');
      return false;
    }

    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      setLocalError('File type not allowed. Please upload PDF, TXT, JPG, or PNG');
      return false;
    }

    if (selectedFile.size > MAX_SIZE) {
      setLocalError('File size exceeds 10MB limit');
      return false;
    }

    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (validateFile(droppedFile)) {
      setFile(droppedFile);
      setLocalError('');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (validateFile(selectedFile)) {
      setFile(selectedFile);
      setLocalError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateFile(file)) {
      return;
    }

    try {
      const exam = await uploadExam(file);
      
      // Redirect to evaluation form with exam data
      navigate(`/upload`, {
        state: { exam },
      });
    } catch (err) {
      console.error('Upload error:', err);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h1>Upload Exam File</h1>
        <p className="upload-subtitle">
          Upload your exam (PDF, TXT, JPG, PNG) - Max 10MB
        </p>

        {(error || localError) && (
          <div className="error-message">{error || localError}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div
            className={`drag-drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-input"
              onChange={handleFileChange}
              accept=".pdf,.txt,.jpg,.jpeg,.png"
              style={{ display: 'none' }}
              disabled={loading}
            />
            <label htmlFor="file-input" className="drag-drop-label">
              <div className="icon">📁</div>
              {file ? (
                <>
                  <p className="file-name">✓ {file.name}</p>
                  <p className="file-size">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                  <p className="change-file">Click to change file</p>
                </>
              ) : (
                <>
                  <p className="main-text">
                    Drag and drop your file here
                  </p>
                  <p className="sub-text">or click to select</p>
                </>
              )}
            </label>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-large"
            disabled={!file || loading}
          >
            {loading ? 'Uploading...' : 'Upload & Continue'}
          </button>
        </form>

        <div className="upload-info">
          <h3>Supported Formats:</h3>
          <ul>
            <li>📄 PDF - Digital exam sheets</li>
            <li>📝 TXT - Text-based answers</li>
            <li>🖼️ JPG/PNG - Scanned/handwritten exams</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
