import React, { useState, useEffect } from 'react';
import '../App.css';

function Account() {

  const [apiStatus, setApiStatus] = useState('Checking...');

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
          setApiStatus('Connected ✓');
        }
      } catch (error) {
        setApiStatus('Disconnected ✗');
      }
    };

    checkHealth();
  }, [API_URL]);


  return (
    <div className="App">
      <header className="App-header">
        <h1>Fusion Cyber Chatbot</h1>
        <p>API Status: <strong>{apiStatus}</strong></p>
      </header>

      <main className="App-main">
        <div className="chat-container">
            This is where the user will change their account details
        </div>
      </main>
    </div>
  );
}

export default Account;
