import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function MessagesPage() {
    const { userId } = useParams();
    const [messages, setMessages] = useState([]);
    const [username, setUsername] = useState('');

    useEffect(() => {
        // Fetch user details
        fetch(`http://127.0.0.1:8000/network/api/users/${userId}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        })
        .then(response => response.json())
        .then(data => {
            setUsername(data.username);
        })
        .catch(console.error);

        // Fetch messages and sort them
        fetch(`http://127.0.0.1:8000/network/api/messages/by_user/?user_id=${userId}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        })
        .then(response => response.json())
        .then(data => {
            const sortedMessages = data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            setMessages(sortedMessages);
        })
        .catch(console.error);
    }, [userId]);

    const formatDate = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    return (
        <div className="container mt-5">
            <div className="card p-4">
                <h2>Messages: {username}</h2>
                {messages.map(message => (
                    <div key={message.id} className="mb-3">
                        <p>{formatDate(message.timestamp)} From {message.sender_details.username} to {message.receiver_details.username}: {message.message}</p>
                    </div>
                ))}
                <div className="text-center mt-4">
                    <Link to="/" className="btn btn-custom">Hide Messages</Link>
                </div>
            </div>
        </div>
    );
}

export default MessagesPage;
