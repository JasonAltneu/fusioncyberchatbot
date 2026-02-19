import React, { useState, useEffect } from 'react';
import '../App.css';

function Sidebar() {
  const [conversations, setConversations] = useState([]);
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const loadConversations = async () => {
      try {
        // history endpoint is POST with no payload
        const res = await fetch(`${API_URL}/history`, { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          setConversations(data.names || []);
        }
      } catch (err) {
        console.error('failed to fetch conversations', err);
      }
    };

    loadConversations();
  }, [API_URL]);

  return (
    <div className = "sidebar" style={{ flex: 1, textAlign: 'left' }}>
      <h2>Conversations</h2>
        {conversations.map((c) => (
          <div key={c.id}>
            {c.initial_prompt}
          </div>
        ))}
    </div>
  );
}

export default Sidebar;