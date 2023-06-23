import React, { useEffect, useState, useContext } from 'react';
import AppContext from './AppContext';


const NPCSelector = () => {
  const [NPCs, setNPCs] = useState([]);
  const [selectedNPC, setSelectedNPC] = useState('');

  const {update_npc_name, world_name} = useContext(AppContext);


  // Fetch the list of NPCs from the API
  useEffect(() => {
    fetchNPCs();
  }, []);


  const fetchNPCs = async () => {
    try {
        console.log('npc selector world_name: ', world_name)
        const response = await fetch('http://127.0.0.1:8002/get_npcs_in_world', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'world_name':world_name})
        });
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        const data = await response.json();
        console.log(data.npcs);
        setNPCs(data.npcs);
    } catch (error) {
      console.error('Error fetching NPCs:', error);
    }
  };

  const handleSelectChange = (event) => {
    setSelectedNPC(event.target.value);
    update_npc_name(event.target.value);
  };

  return (
    <div>
      <h2>NPC Selector</h2>
      <select value={selectedNPC} onChange={handleSelectChange}>
        <option value="">Select an NPC</option>
        {NPCs.map((NPC) => (
          <option key={NPC} value={NPC}>
            {NPC}
          </option>
        ))}
      </select>
    </div>
  );
};

export default NPCSelector;