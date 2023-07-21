
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/WorldCreator.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';


const WorldCreator = () => {
  const [worlds, setWorlds] = useState([]);
  const [users, setUsers] = useState([]);
  const [currentWorld, setCurrentWorld] = useState(null);
  const [description, setDescription] = useState('');
  const [newWorldName, setNewWorldName] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [showPopup, setShowPopup] = useState(false);
  const [showPopupNewUser, setShowPopupNewUser] = useState(false);
  const [editorOption, setEditorOption] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [currentScene, setCurrentScene] = useState({
    scene_name: "",
    previous_scene: "",
    NPCs: {},
    objectives: [],
    narration_intro: "",
    narration_outro: ""
  });
  const [npcs, setNpcs] = useState([]);
  const [currentNpc, setCurrentNpc] = useState(null);
  const [npcPersonality, setNpcPersonality] = useState('');
  const [sceneNpcName, setSceneNpcName] = useState('');
  const [sceneNpcPrompt, setSceneNpcPrompt] = useState('');
  const [newNpcName, setNewNpcName] = useState('');
  const [newNpcPersonality, setNewNpcPersonality] = useState('');
  const [isNewScene, setIsNewScene] = useState(true);
  const [playGameWorld, setPlayGameWorld] = useState('')
  const [playGameUser, setPlayGameUser] = useState('')
  const [playTestSceneWorld, setPlayTestSceneWorld] = useState('')
  const [playTestSceneScene, setPlayTestSceneScene] = useState('')
  const [playTestScenes, setPlayTestScenes] = useState([])


  useEffect(() => {
    getAllWorlds()
    getAllUsers()
  }, []);

  const getAllWorlds = () => {
    axios.get('http://127.0.0.1:8002/get_all_worlds')
      .then(res => setWorlds(res.data.worlds))
      .catch(err => console.log(err));
  };

  const getAllUsers = () => {
    axios.get('http://127.0.0.1:8002/get_all_users')
    .then(res => {
        // console.log(res.data)
        setUsers(res.data);
    })
    .catch(err => console.log(err));
  };


  const playGame = () => {
    if (playGameUser && playGameWorld) {
        axios.post('http://127.0.0.1:8002/play_world_in_renpy',{'world_name':playGameWorld,"user_name":playGameUser})
        .catch(err => console.log(err))
    }
  };

  const playTestScene = () => {
    console.log(playTestSceneWorld)
    console.log(playTestSceneScene)
    axios.post('http://127.0.0.1:8002/play_test_scene_in_renpy', {
      'world_name': playTestSceneWorld,
      'scene_id': playTestSceneScene
    })
    .catch(err => console.log(err));
  }

  const createWorld = () => {
    setCurrentWorld({world_name: newWorldName, world_description: '' });
    setNewWorldName('');
    setShowPopup(false);
  };

  const createUser = () => {
    setUsers(prevUsers => [...prevUsers, {user_name: newUserName}]);
    setPlayGameUser(newUserName);
    setNewUserName('');
    setShowPopupNewUser(false);
    axios.post('http://127.0.0.1:8002/upsert_user', {'user_name': newUserName,})
  };

  const updatePlayTestWorld = (world_name) => {
    setPlayTestSceneWorld(world_name);
    axios.post('http://127.0.0.1:8002/get_all_scenes_in_order/', { world_name: world_name })
    .then(res => {
    setPlayTestScenes(res.data.scenes);
    })
  };

  
 

  const updateScenes = () => {
    if (currentWorld) {
        axios.post('http://127.0.0.1:8002/get_all_scenes_in_order/', { world_name: currentWorld.world_name })
          .then(res => setScenes(res.data.scenes))
          .catch(err => console.log(err));
      }
  };

  const handleSceneEditor = () => {
    updateScenes();
    updateNpcs();
    setEditorOption('scene');
  };

  const updateNpcs = () => {
    if (currentWorld) {
        axios.post('http://127.0.0.1:8002/get_npcs_in_world/', { world_name: currentWorld.world_name })  
          .then(res => {
              console.log(res.data)
              setNpcs(res.data)   
          })
          .catch(err => console.log(err));
      }
  };

  const handleNpcEditor = () => {
    updateNpcs();
    setEditorOption('npc');
  };


  const saveWorldChanges = () => {
    const updatedWorld = {...currentWorld, world_description: description};
    axios.post('http://127.0.0.1:8002/upsert_world/', updatedWorld)
      .then(res => console.log(res))
      .catch(err => console.log(err));
  };

  const saveScene = () => {
    const updatedScene = {
        ...currentScene,
        objectives: currentScene.objectives,
        NPCs: {
        ...currentScene.NPCs,
        [sceneNpcName]: {
          ...currentScene.NPCs[sceneNpcName],
          scene_npc_prompt: sceneNpcPrompt
        }}}
    axios.post('http://127.0.0.1:8002/update_scene/', updatedScene)
      .then(res => console.log(res))
      .catch(err => console.log(err));
  }

  const saveNpc = () => {
    const updatedNpc = {...currentNpc, personality: npcPersonality}
    console.log(updatedNpc)
    axios.post('http://127.0.0.1:8002/upsert_npc/',updatedNpc)
    .then(res=>console.log(res))
    .catch(err=>console.log(err))
  }

  const createNewScene = () => {
    const newScene = { 
      world_name: currentWorld.world_name, 
      scene_name: currentScene.scene_name, 
      previous_scene: currentScene.previous_scene,
      NPCs: {
        ...currentScene.NPCs,
        [sceneNpcName]: {
          ...currentScene.NPCs[sceneNpcName],
          scene_npc_prompt: sceneNpcPrompt
        }},
      objectives: currentScene.objectives,
      narration_intro: currentScene.narration_intro,
      narration_outro: currentScene.narration_outro
    };
    console.log(newScene)
    axios.post('http://127.0.0.1:8002/insert_scene/', newScene)
      .then(res => {
        console.log(res);
        setCurrentScene({
          scene_name: "",
          previous_scene: "",
          NPCs: {},
          objectives: [],
          narration_intro: "",
          narration_outro: ""
        });
        handleSceneEditor();
      })
      .catch(err => console.log(err));
  };

  const createNewNpc = () => {
    const newNpc = { world_name: currentWorld.world_name, npc_name: newNpcName, personality: newNpcPersonality };
    axios.post('http://127.0.0.1:8002/upsert_npc/', newNpc)
        .then(res => {
            console.log(res);
            setNewNpcName('');
            setNewNpcPersonality('');
            // Optionally, refresh your list of NPCs here
            handleNpcEditor();
        })
        .catch(err => console.log(err));
  }

  // After picking a world you have to pick an Editor
  if (currentWorld && editorOption === null) {
    return (
      <div>
        <button onClick={() => setCurrentWorld(null)}>Back</button>
        <h1>{currentWorld.world_name}</h1>
        <button onClick={() => setEditorOption('world')}>World Editor</button>
        <button onClick={handleSceneEditor}>Scene Editor</button>
        <button onClick={handleNpcEditor}>NPC Editor</button>
      </div>
    );
  }

  // The world editor
  if (editorOption === 'world') {
    return (
        <div className="WorldCreator">
        <button onClick={() => setEditorOption(null)}>Back</button>
          <div className="editor">
            <h1>{currentWorld.world_name}</h1>
            <div className="input-group">
              <label>World Description</label>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)}></textarea>
            </div>
            <button className="update-button" onClick={saveWorldChanges}>Save Changes to World</button>
          </div>
        </div>
      );
  }

  // the scene editor
  if (editorOption === 'scene') {
    const addNewObjective = () => {
        setCurrentScene({ ...currentScene, objectives: [...currentScene.objectives, ''] });
    };

    const handleObjectiveChange = (index, newObjective) => {
        let objectives = [...currentScene.objectives];
        objectives[index] = newObjective;
        setCurrentScene({ ...currentScene, objectives });
    };

    return (
        <div className="WorldCreator">
            <button onClick={() => setEditorOption(null)}>Back</button>
            <h1>Select a Scene:</h1>
            {scenes.map((scene) => (
                <button key={scene._id} onClick={() => {
                    setCurrentScene(scene);
                    console.log(scene)
                    const npcName = scene.NPCs ? Object.keys(scene.NPCs)[0] : '';
                    const npcPrompt = scene.NPCs && scene.NPCs[npcName] ? scene.NPCs[npcName].scene_npc_prompt : '';
                    setSceneNpcName(npcName);
                    setSceneNpcPrompt(npcPrompt);
                    setIsNewScene(false);
                }}>
                    {scene.scene_name}
                </button>
            ))}
            <button onClick={() => {
                setCurrentScene({
                    scene_name: "",
                    previous_scene: "",
                    NPCs: {},
                    objectives: [],
                    narration_intro: "",
                    narration_outro: ""
                });
                setSceneNpcName("")
                setSceneNpcPrompt("")
                setIsNewScene(true);
            }}>
                Create a new Scene
            </button>
            {!isNewScene ? (
                <div>
                    <h1>{currentScene.scene_name}</h1>
                     <div className="editor">
                     <div className="input-group">
                     <label>Scene ID (read-only)</label>
                     <input type="text" value={currentScene._id || ''} readOnly />
                    </div>
                    <div className="input-group">
                        <label>Scene Name</label>
                        <input type="text" value={currentScene.scene_name || ''} onChange={(e) => setCurrentScene({ ...currentScene, scene_name: e.target.value })} />
                    </div>
                    <div className="input-group">
                        <label>Previous Scene</label>
                        <select 
                            value={currentScene.previous_scene || ''} 
                            onChange={(e) => setCurrentScene({ ...currentScene, previous_scene: e.target.value })}>
                            <option value="">Select previous scene</option>
                            {scenes.map((scene, index) => (
                            <option key={index} value={scene.scene_name}>{scene.scene_name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="input-group">
                        <label>NPC Name</label>
                        <select 
                            value={currentScene.npc_name || ''} 
                            onChange={(e) => setCurrentScene({ ...currentScene, npc_name: e.target.value })}>
                            <option value="">Select NPC</option>
                            {npcs.map((npc, index) => (
                            <option key={index} value={npc.npc_name}>{npc.npc_name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="input-group">
                        <label>Scene NPC Prompt</label>
                        <textarea value={sceneNpcPrompt} onChange={(e) => setSceneNpcPrompt(e.target.value)}></textarea>
                    </div>
                    {currentScene.objectives.map((objective, index) => (
                    <div key={index} className="input-group">
                        <label>Objective {index + 1}</label>
                        <input
                        type="text"
                        value={objective}
                        onChange={(e) => handleObjectiveChange(index, e.target.value)}
                        />
                        <FontAwesomeIcon
                            icon={faTrash}
                            onClick={() => {
                                const updatedObjectives = [...currentScene.objectives];
                                updatedObjectives.splice(index, 1);
                                setCurrentScene({ ...currentScene, objectives: updatedObjectives });
                        }}/>
                    </div>
                    ))}
                    <button onClick={addNewObjective}>Add New Objective</button>
                    <div className="input-group">
                        <label>Narration Intro</label>
                        <textarea value={currentScene.narration_intro || ''} onChange={(e) => setCurrentScene({ ...currentScene, narration_intro: e.target.value })}></textarea>
                    </div>
                    <div className="input-group">
                        <label>Narration Outro</label>
                        <textarea value={currentScene.narration_outro || ''} onChange={(e) => setCurrentScene({ ...currentScene, narration_outro: e.target.value })}></textarea>
                    </div>
                    <button onClick={saveScene}>Save Updates to Scene</button>
                    </div>
                </div>
            ) : (
                <div>
                    <h1>Create a new Scene</h1>
                    <div className="editor">
                        <div className="input-group">
                            <label>Scene Name</label>
                            <input type="text" value={currentScene.scene_name || ''} onChange={(e) => setCurrentScene({ ...currentScene, scene_name: e.target.value })} />
                        </div>
                        <div className="input-group">
                            <label>Previous Scene</label>
                            <select 
                                value={currentScene.previous_scene || ''} 
                                onChange={(e) => setCurrentScene({ ...currentScene, previous_scene: e.target.value })}>
                                <option value="">Select previous scene</option>
                                {scenes.map((scene, index) => (
                                <option key={index} value={scene.scene_name}>{scene.scene_name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="input-group">
                            <label>NPC Name</label>
                            <select 
                                value={currentScene.npc_name || ''} 
                                onChange={(e) => setCurrentScene({ ...currentScene, npc_name: e.target.value })}>
                                <option value="">Select NPC</option>
                                {npcs.map((npc, index) => (
                                <option key={index} value={npc.npc_name}>{npc.npc_name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="input-group">
                            <label>Scene NPC Prompt</label>
                            <textarea value={sceneNpcPrompt} onChange={(e) => setSceneNpcPrompt(e.target.value)}></textarea>
                        </div>
                        {currentScene.objectives.map((objective, index) => (
                        <div key={index} className="input-group">
                            <label>Objective {index + 1}</label>
                            <input
                            type="text"
                            value={objective}
                            onChange={(e) => handleObjectiveChange(index, e.target.value)}
                            />
                            <FontAwesomeIcon
                                icon={faTrash}
                                onClick={() => {
                                    const updatedObjectives = [...currentScene.objectives];
                                    updatedObjectives.splice(index, 1);
                                    setCurrentScene({ ...currentScene, objectives: updatedObjectives });
                            }}/>
                        </div>
                        ))}
                        <button onClick={addNewObjective}>Add New Objective</button>
                        <div className="input-group">
                            <label>Narration Intro</label>
                            <textarea value={currentScene.narration_intro || ''} onChange={(e) => setCurrentScene({ ...currentScene, narration_intro: e.target.value })}></textarea>
                        </div>
                        <div className="input-group">
                            <label>Narration Outro</label>
                            <textarea value={currentScene.narration_outro || ''} onChange={(e) => setCurrentScene({ ...currentScene, narration_outro: e.target.value })}></textarea>
                        </div>
                    </div>
                    <button onClick={createNewScene}>Create Scene</button>
                </div>
            )}
        </div>
    );
}

  if (editorOption === 'npc') {
    return (
        <div className="WorldCreator">
            <button onClick={() => setEditorOption(null)}>Back</button>
            <h1>Select a NPC:</h1>
            {npcs.map((npc) => (
                <button key={npc._id} onClick={() => {setCurrentNpc(npc); setNpcPersonality(npc.personality !== undefined ? npc.personality : '')}}>
                {npc.npc_name}
                </button>
            ))}
            <button onClick={() => {setCurrentNpc(null); setNpcPersonality('');}}>Create a new NPC</button>
            {currentNpc ? (
            <div>
                <h1>{currentNpc.npc_name}</h1>
                <div className="input-group">
                <label>Personality</label>
                <textarea value={npcPersonality} onChange={(e) => setNpcPersonality(e.target.value)}></textarea>
                </div>
                <button onClick={saveNpc}>Save Updates to NPC</button>
            </div>
            ) : (
            <div>
                <h1>Create a new NPC</h1>
                <div className="input-group">
                    <label>NPC Name</label>
                    <input type="text" value={newNpcName} onChange={(e) => setNewNpcName(e.target.value)} />
                </div>
                <div className="input-group">
                    <label>Personality</label>
                    <textarea value={newNpcPersonality} onChange={(e) => setNewNpcPersonality(e.target.value)}></textarea>
                </div>
                <button onClick={createNewNpc}>Create NPC</button>
            </div>
            )}
        </div>
    );
  }

  return (
    <div>
      <h1><span style={{ textDecoration: 'underline' }}>Select a world to edit</span></h1>
      {worlds.map((world) => (
        <button key={world._id} onClick={() => {setCurrentWorld(world); setDescription(world.world_description)}}>
          {world.world_name}
        </button>
      ))}
      <button onClick={() => setShowPopup(true)}>Create a new world</button>
      {showPopup && (
        <div>
          <input
            type="text"
            placeholder="World name"
            value={newWorldName}
            onChange={(e) => setNewWorldName(e.target.value)}
          />
          <button onClick={createWorld}>Create</button>
        </div>
      )}

      
      <h1><span style={{ textDecoration: 'underline' }}>Play Your Game Where You Left Off</span></h1>
      <div>
      <select onChange={event => setPlayGameWorld(event.target.value)}>
      <option value="">Choose World</option>
      {worlds.map((world, index) => (
          <option key={index} value={world.world_name}>
          {world.world_name}
          </option>
      ))}
      </select>
        <select onChange={event => setPlayGameUser(event.target.value)}>
        <option value="">Choose User</option>
            {users.map((user, index) => (
                <option key={index} value={user.user_name}>
                {user.user_name}
                </option>
            ))}
        </select>
        <button onClick={() => playGame()}>Play World</button>
        <button onClick={() => setShowPopupNewUser(true)}>Create a new user</button>
      {showPopupNewUser && (
        <div>
          <input
            type="text"
            placeholder="User name"
            value={newUserName}
            onChange={(e) => setNewUserName(e.target.value)}
          />
          <button onClick={createUser}>Create</button>
        </div>
      )}
      </div>


      <h1><span style={{ textDecoration: 'underline' }}>Play Test a Scene as a Temporary User</span></h1>
        <select onChange={event => updatePlayTestWorld(event.target.value)}>
        <option value="">Choose World</option>
        {worlds.map((world, index) => (
            <option key={index} value={world.world_name}>
            {world.world_name}
            </option>
        ))}
        </select>
        <select onChange={event => setPlayTestSceneScene(event.target.value)}>
        <option value="">Choose Scene</option>
            {playTestScenes.map((scene, index) => (
            <option key={index} value={scene._id}>
                {scene.scene_name}
            </option>
            ))}
        </select>
        <button onClick={() => playTestScene()}>Play Test Scene</button>


    </div>
  );
};

export default WorldCreator;