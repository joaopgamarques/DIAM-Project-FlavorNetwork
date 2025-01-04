import React, { useState, useEffect } from 'react';

function Message({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [receiver, setReceiver] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/api/users/')
      .then(response => response.json())
      .then(data => setUsers(data.filter(user => user.id !== currentUser.id)));
  }, [currentUser]);

  const sendMessage = () => {
    console.log('Sending message:', message, 'to', receiver);
  };

  return (
    <div>
      <select value={receiver} onChange={e => setReceiver(e.target.value)}>
        <option>Select a User</option>
        {users.map(user => (
          <option key={user.id} value={user.id}>{user.username}</option>
        ))}
      </select>
      <textarea
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="Enter your message here"
      ></textarea>
      <button onClick={sendMessage}>Send Message</button>
    </div>
  );
}

export default Message;
