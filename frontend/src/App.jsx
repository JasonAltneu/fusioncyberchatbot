import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Account from './Account';

function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setResponse('');

    try {
      const res = await fetch(`${API_URL}/chat?message=${encodeURIComponent(message)}`, {
        method: 'POST',
      });

      if (res.ok) {
        const data = await res.json();
        setResponse(data.reply);
      } else {
        setResponse('Error: Could not connect to the server.');
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
      setMessage('');
    }
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Fusion Cyber Chatbot</h1>
          <p>API Status: <strong>{apiStatus}</strong></p>
          <nav className="App-nav">
            <Link to="/">Home</Link> |
            <Link to="/account">Account</Link>
          </nav>
        </header>

        <main className="App-main">
          <Routes>
            <Route
              path="/"
              element={
                <div className="chat-container">
                  <form onSubmit={handleSendMessage}>
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Type your message..."
                      disabled={loading}
                    />
                    <button type="submit" disabled={loading}>
                      {loading ? 'Sending...' : 'Send'}
                    </button>
                  </form>

                  {response && (
                    <div className="response">
                      <strong>Response:</strong>
                      <p>{response}</p>
                    </div>
                  )}
                </div>
              }
            />

            <Route path="/account" element={<Account />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
