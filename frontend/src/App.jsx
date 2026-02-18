import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Account from './Account';
import Sidebar from './CustomComponents/Sidebar';

function App() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState([]);        // conversation history
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('Checking...');

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  // Check API health and load history on component mount
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

    const loadHistory = async () => {
      try {
        const res = await fetch(`${API_URL}/history`);
        if (res.ok) {
          const data = await res.json();
          setHistory(data.history || []);
        }
      } catch {}
    };

    checkHealth();
    loadHistory();
  }, [API_URL]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat?message=${encodeURIComponent(message)}`, {
        method: 'POST',
      });

      if (res.ok) {
        const data = await res.json();
        // update history array instead of a flat string
        setHistory((h) => [...h, { user: message, bot: data.reply }]);
      } else {
        // could put errors into history too
      }
    } catch (error) {
      console.error(error);
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
          <Sidebar/>
          <Routes>
            <Route
              path="/"
              element={
                <div className="chat-container" style={{flex: 4}}>
                  <div className="history">
                    {history.map((turn, idx) => (
                      <div key={idx} className="turn">
                        <div className="user">You: {turn.user}</div>
                        <div className="bot">Bot: {turn.bot}</div>
                      </div>
                    ))}
                  </div>

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
