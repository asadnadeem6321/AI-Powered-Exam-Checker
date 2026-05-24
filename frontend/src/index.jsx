import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

// Defensive: ignore runtime errors originating from browser extensions (chrome-extension://)
// These errors are injected into the page context by user-installed extensions and
// can surface as uncaught runtime errors in the React dev overlay. We silently
// swallow such extension-originated errors to avoid confusing developers and users.
if (typeof window !== 'undefined' && window.addEventListener) {
  window.addEventListener(
    'error',
    (e) => {
      try {
        if (e && e.filename && typeof e.filename === 'string' && e.filename.startsWith('chrome-extension://')) {
          e.preventDefault();
          return true;
        }
      } catch (_err) {
        // ignore
      }
      return false;
    },
    true
  );

  window.addEventListener(
    'unhandledrejection',
    (ev) => {
      try {
        const reason = ev && ev.reason;
        const stack = reason && (reason.stack || reason.toString());
        if (stack && typeof stack === 'string' && stack.includes('chrome-extension://')) {
          ev.preventDefault();
          return true;
        }
      } catch (_err) {
        // ignore
      }
      return false;
    },
    true
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
