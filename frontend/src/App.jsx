import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Account from './Account';
import Sidebar from './CustomComponents/Sidebar';



function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('Checking...');
  const [activeChat, setActiveChat] = useState(0)

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

  const handleSetActive = (val) =>{
    setActiveChat(val)
  }

  const handleSetMessages = (val) => {
    const normalized = val.map(item => ({
      uid: item.id,
      time: new Date(item.last_updated),
      text: item.message,
      from: item.sender
    }));
    normalized.sort((a,b) => {
      return new Date(a.time) - new Date(b.time);
    })
    const chatString = normalized
      .map(msg => `${msg.from}: ${msg.text}`)
      .join("\n");

    // show the string to the user
    setResponse(chatString);
  }

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);

    try {
      // build URL with optional chat_id parameter
      const url = new URL(`${API_URL}/chat`);
      url.searchParams.set('message', message);
      if (activeChat && activeChat !== 0) {
        url.searchParams.set('chat_id', activeChat);
      }

      const res = await fetch(url.toString(), {
        method: 'POST',
      });

      if (res.ok) {
        const data = await res.json();
        setResponse( response + "\nyou: "+ message + "\nbot: " +data.reply +"\n");
        // if server created a new chat, update activeChat
        if (data.chat_id && activeChat === 0) {
          setActiveChat(data.chat_id);
        }
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
          <Sidebar
            setHandler = {handleSetActive}
            setHistory={handleSetMessages}/>
          <Routes>
            <Route
              path="/"
              element={
                <div className="chat-container" style={{flex: 4}}>
                  <div>Active Chat: {activeChat}</div>
                  <textarea className='response' placeholder='Type Something Below' value={response} contentEditable='false'/>
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
