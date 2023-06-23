import { useState, useEffect } from "react";
import "./App.css";
import UserSelector from './UserSelector';
import AppContext from './AppContext';
import NPCChatWindow from "./NPCChatWindow";
import GameDesignerChatWindow from "./GameDesignerChatWindow";


function App() {
  //Track user_name, world_name, and npc_name at this level
  const [user_name, set_user_name] = useState('');
  const [world_name, set_world_name] = useState('');
  const [npc_name, set_npc_name] = useState('');
  // Functions to update variables
  const update_user_name = (new_user_name) => {
    set_user_name(new_user_name);
  };
  const update_world_name = (new_world_name) => {
    set_world_name(new_world_name);
  };
  const update_npc_name = (new_npc_name) => {
    set_npc_name(new_npc_name);
  };

  
  async function handleClick(world_name) {
    const response = await fetch('http://127.0.0.1:8004/extract_all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 'world_name': world_name }),
    });
  
    if (!response.ok) {
      throw new Error('Network response was not ok.');
    }
  }
  
    

  return (
    <div className="app">
      <div className="app-container">
        <AppContext.Provider value={{update_user_name, update_world_name, update_npc_name, world_name}}>
          <div className="selectors">
            <UserSelector />
          </div>
          <div className="game-designer-chat-window">
            <p>Chat with the 'Game Designer AI'.</p>
            <p>Tell it what types of characters you want to create!</p>
            <GameDesignerChatWindow world_name={world_name} />
          </div>
          <div>
            <button onClick={() => handleClick(world_name)}>Extract NPCs</button>
          </div>
          <div className="npc-chat-window">
            <p>Select the NPC you want to chat with.</p>
            <p>--</p>
            <NPCChatWindow user_name={user_name} world_name={world_name} npc_name={npc_name}/>
          </div>
        </AppContext.Provider>
      </div>
    </div>
  );
}

export default App;