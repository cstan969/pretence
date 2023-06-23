import React, { useEffect, useState, useContext} from 'react';
import WorldSelector from './WorldSelector'; // Import the WorldSelector component
import AppContext from './AppContext';

const UserSelector = () => {
  const [usernames, setUsernames] = useState([]);
  const [selectedUsername, setSelectedUsername] = useState('');
  const [newUsername, setNewUsername] = useState('');
  const [userSelected, setUserSelected] = useState(false);

  const {update_user_name, update_world_name, update_npc_name, world_name} = useContext(AppContext);


  // Fetch the list of usernames from the API
  useEffect(() => {
    fetchUsernames();
  }, []);

  const fetchUsernames = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/get_all_users', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      const data = await response.json();
      setUsernames(data.users);
    } catch (error) {
      console.error('Error fetching usernames:', error);
    }
  };

  const handleSelectChange = (event) => {
    setSelectedUsername(event.target.value);
    update_user_name(event.target.value);
    setUserSelected(true); // Set userSelected to true when a user is selected
  };

  const handleInputChange = (event) => {
    setNewUsername(event.target.value);
  };

  const handleCreateUser = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/upsert_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'user_name': newUsername }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      console.log('new username to add: ', newUsername);
      setUsernames([...usernames, newUsername]);
      setNewUsername('');
    } catch (error) {
      console.error('Error creating username:', error);
    }
  };

  return (
    <AppContext.Provider value={{update_world_name, update_npc_name, world_name}}>
      <div>
          <h2>User Selector</h2>
          <select value={selectedUsername} onChange={handleSelectChange}>
            <option value="">Select a username</option>
            {usernames.map((username) => (
              <option key={username} value={username}>
                {username}
              </option>
            ))}
          </select>
          <br />
          <input
            type="text"
            value={newUsername}
            onChange={handleInputChange}
            placeholder="Enter a new username"
          />
          <button onClick={handleCreateUser}>Create</button>

          {userSelected && <WorldSelector />} {/* Render WorldSelector only when a user is selected */}
      </div>
    </AppContext.Provider>
  );
};

export default UserSelector;