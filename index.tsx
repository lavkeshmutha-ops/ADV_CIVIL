
import React from 'react';
import { createRoot } from 'react-dom/client';

/**
 * Note for the User:
 * This index.tsx file is a web-based landing page for the environment.
 * The actual LexGuardian application is built in Python (App.py) for local desktop use.
 */

const App = () => {
  return (
    <div style={{
      fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      backgroundColor: '#2C3E50',
      color: 'white',
      textAlign: 'center',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        padding: '40px',
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        maxWidth: '600px'
      }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⚖️ LexGuardian</h1>
        <p style={{ fontSize: '1.2rem', color: '#BDC3C7', marginBottom: '2rem' }}>
          Advocate Case Assistant: Desktop Software
        </p>
        <div style={{ textAlign: 'left', backgroundColor: '#34495E', padding: '20px', borderRadius: '8px' }}>
          <h3 style={{ marginTop: 0, color: '#1ABC9C' }}>Implementation Ready:</h3>
          <ul style={{ lineHeight: '1.6' }}>
            <li><strong>Desktop Core:</strong> Tkinter-based GUI (App.py)</li>
            <li><strong>Local Database:</strong> MySQL Schema (schema.sql)</li>
            <li><strong>AI Logic:</strong> Gemini 3 Pro Integration (ai_service.py)</li>
            <li><strong>Modules:</strong> Client Management & Modern Settings</li>
          </ul>
        </div>
        <p style={{ marginTop: '2rem', fontSize: '0.9rem', color: '#95A5A6' }}>
          To run locally: Ensure MySQL is running, set your API_KEY, and execute <code>python App.py</code>.
        </p>
      </div>
    </div>
  );
};

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
}
