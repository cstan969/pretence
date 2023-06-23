import React, { useEffect, useState, useContext } from 'react';
import NPCSelector from './NpcSelector'; // Import the NPCSelector component
import AppContext from './AppContext';

const WorldSelector = () => {
  const [worlds, setWorlds] = useState([]);
  const [selectedWorld, setSelectedWorld] = useState('');
  const [newWorld, setNewWorld] = useState('');

  const {update_world_name,update_npc_name,world_name} = useContext(AppContext);


  // Fetch the list of worlds from the API
  useEffect(() => {
    fetchWorlds();
  }, []);

  const fetchWorlds = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/get_all_worlds', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      const data = await response.json();
      console.log(data.worlds);
      setWorlds(data.worlds);
    } catch (error) {
      console.error('Error fetching worlds:', error);
    }
  };

  const handleSelectChange = (event) => {
    setSelectedWorld(event.target.value);
    update_world_name(event.target.value);
  };

  const handleInputChange = (event) => {
    setNewWorld(event.target.value);
  };

  const handleCreateWorld = async () => {
    try {
      console.log('New world to add: ', newWorld);
      const response = await fetch('http://127.0.0.1:8002/upsert_world', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'world_name': newWorld }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      console.log('New world to add: ', newWorld);
      setWorlds([...worlds, newWorld]);
      setNewWorld('');
    } catch (error) {
      console.error('Error creating world:', error);
    }
  };

  return (
    <AppContext.Provider value={{update_npc_name, world_name}}>
      <div>
        <h2>World Selector</h2>
        <select value={selectedWorld} onChange={handleSelectChange}>
          <option value="">Select a world</option>
          {worlds.map((world) => (
            <option key={world} value={world}>
              {world}
            </option>
          ))}
        </select>
        <br />
        <input
          type="text"
          value={newWorld}
          onChange={handleInputChange}
          placeholder="Enter a new world name"
        />
        <button onClick={handleCreateWorld}>Create</button>

        {selectedWorld && <NPCSelector selectedWorld={selectedWorld} />}
      </div>
    </AppContext.Provider>
  );
};

export default WorldSelector;