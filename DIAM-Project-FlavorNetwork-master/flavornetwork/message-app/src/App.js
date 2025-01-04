import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import UsersDropdown from './UsersDropdown';
import MessagesPage from './MessagesPage';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [senderId, setSenderId] = useState('');
  const [receiverId, setReceiverId] = useState('');
  const [message, setMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const handleMessageSend = () => {
    const messageData = {
      sender: senderId,
      receiver: receiverId,
      message: message
    };

    fetch('http://127.0.0.1:8000/network/api/messages/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(messageData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      setStatusMessage('Message sent successfully!');
      setMessage('');
      setTimeout(() => {
        setStatusMessage('');
      }, 3000);
    })
    .catch(error => {
      console.error('Error:', error);
      setStatusMessage('Failed to send message.');
    });
  };

  return (
    <Router>
      <div className="container mt-5">
        <h1 className="text-center mb-4">Message Center</h1>
        <div className="card p-4">
          <form>
            <div className="mb-3">
              <UsersDropdown
                label="Sender:"
                value={senderId}
                onChange={e => setSenderId(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <UsersDropdown
                label="Receiver:"
                value={receiverId}
                onChange={e => setReceiverId(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <textarea
                className="form-control"
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Enter your message here"
                rows="3"
              />
            </div>
            <div className="text-center">
              <button type="button" className="btn btn-custom" onClick={handleMessageSend} style={{ marginRight: '20px' }}>Send Message</button>
              <Link to={`/messages/${senderId}`} className="btn btn-custom">View Messages</Link>
            </div>
          </form>
        </div>
        <Routes>
          <Route path="/messages/:userId" element={<MessagesPage />} />
        </Routes>
        <br/>
        {statusMessage && <div className="alert alert-success">{statusMessage}</div>}
      </div>
    </Router>
  );
}

export default App;
