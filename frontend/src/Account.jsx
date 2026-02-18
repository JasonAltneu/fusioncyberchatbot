import React from 'react';

function Account() {
  return (
    <div className="account-page" style={{flex: 4}}>
      <h2>Account</h2>
      <form>
        <label>Name: <input name='userName' placeholder='John Doe'/></label>
        <label>Email: <input name='userEmail' placeholder='example@gmail.com'/></label>
      </form>
    </div>
  );
}

export default Account;