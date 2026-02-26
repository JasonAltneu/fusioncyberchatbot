import React, { useState } from 'react';

function Account({ user_parameters = {} }) {
  // initialize state from the passed-in user_parameters object
  const [name, setName] = useState(user_parameters.UserName || '');
  const [email, setEmail] = useState(user_parameters.UserEmail || '');
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const updateUserInfo = async () => {
      try {
        const url = new URL(`${API_URL}/updateinfo`);
        url.searchParams.set('name', name);
        url.searchParams.set('email', email);
        await fetch(url.toString(), {
          method: 'POST',
        });
      } catch (err) {
        console.error('Failed to load user info', err);
      }
  }

  return (
    <div className="account-page" style={{flex: 4}}>
      <h2>Account</h2>
      <form>
        <label>
          Name: 
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="John Doe"
          />
        </label>
        <br />
        <label>
          Email: 
          <input
            type="text"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="example@gmail.com"
          />
        </label>
        <br />
        <button type="button" onClick={e => updateUserInfo()}>Save Information</button>
      </form>
    </div>
  );
}

export default Account;