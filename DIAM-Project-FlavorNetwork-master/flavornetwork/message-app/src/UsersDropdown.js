import React, {useEffect, useState} from 'react';

function UsersDropdown({label, onChange, value}) {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/network/api/users/', {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        })
            .then(response => response.json())
            .then(setUsers)
            .catch(console.error);
    }, []);

    return (
        <div>
            <label>
                {label}
                <select value={value} onChange={onChange}>
                    <option value="">Select a User</option>
                    {users.map(user => (
                        <option key={user.id} value={user.id}>
                            {user.username}
                        </option>
                    ))}
                </select>
            </label>
        </div>
    );
}

export default UsersDropdown;
