
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/WorldCreator.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

import SceneBackgroundImageFileSelector from '../components/SceneBackgroundImageFileSelector';
import SceneMusicFileSelector from './SceneMusicFileSelector.jsx';

const WorldCreator = () => {
  //user variables
  const [users, setUsers] = useState([]);
  const [newUserName, setNewUserName] = useState('');
  //world variables
  const [worlds, setWorlds] = useState([]);
  const [currentWorld, setCurrentWorld] = useState({
    world_name: "",
    world_description: "",
    narration_intro: "",
    narration_outro: ""
  });
  const [worldDescription, setWorldDescription] = useState('');
  const [worldNarrationIntro, setWorldNarrationIntro] = useState('');
  const [worldNarrationOutro, setWorldNarrationOutro] = useState('');

  const [newWorldName, setNewWorldName] = useState('');
  
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
    narration_outro: "",
    background_image_filepath: "",
    music_filepath: ""
  });
  const [previousSceneName, setPreviousSceneName] = useState('')
  const [npcs, setNpcs] = useState([]);
  const [currentNpc, setCurrentNpc] = useState(null);
  const [npcPersonality, setNpcPersonality] = useState('');
  const [npcKnowledge, setNpcKnowledge] = useState('');
  const [sceneNpcName, setSceneNpcName] = useState('');
  const [sceneNpcPrompt, setSceneNpcPrompt] = useState('');
  const sceneNPCs = {
    [sceneNpcName]: {
      scene_npc_prompt: sceneNpcPrompt
    }
  };
  const [newNpcName, setNewNpcName] = useState('');
  const [newNpcPersonality, setNewNpcPersonality] = useState('');
  const [isNewScene, setIsNewScene] = useState(true);
  //play game as user variables
  const [playGameWorld, setPlayGameWorld] = useState('')
  const [playGameUser, setPlayGameUser] = useState('')
  //play test world/scene variables
  const [playTestSceneWorld, setPlayTestSceneWorld] = useState('')
  const [playTestSceneScene, setPlayTestSceneScene] = useState('')
  const [playTestScenes, setPlayTestScenes] = useState([])

  const clearCurrentScene = () => {
    setCurrentScene({
      scene_name: "",
      previous_scene: "",
      NPCs: {},
      objectives: [],
      narration_intro: "",
      narration_outro: "",
      background_image_filepath: "",
      music_filepath: ""
    });
    setSceneNpcName("");
    setSceneNpcPrompt("");
  };


  useEffect(() => {
    getAllWorlds()
    getAllUsers()
  }, []);


  const getAllWorlds = () => {
    axios.get('http://127.0.0.1:8002/get_all_worlds')
      .then(res => {
        setWorlds(res.data.worlds);
      })
      .catch(err => console.log(err));
  };

  const getAllUsers = () => {
    axios.get('http://127.0.0.1:8002/get_all_users')
    .then(res => {
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
    // console.log(playTestSceneWorld)
    // console.log(playTestSceneScene)
    axios.post('http://127.0.0.1:8002/play_test_scene_in_renpy', {
      'world_name': playTestSceneWorld,
      'scene_id': playTestSceneScene
    })
    .catch(err => console.log(err));
  }

  const createWorld = () => {
    setShowPopup(false);
    axios.post('http://127.0.0.1:8002/upsert_world',{'world_name': newWorldName})
    .then(res => {
      setWorlds(prevWorlds => [...prevWorlds, res.data]);
    })
    .catch(err => console.log(err))
    setNewWorldName('');
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
    console.log('currentWorld: ', currentWorld.world_name)
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
    const updatedWorld = {
        ...currentWorld,
        world_description: worldDescription,
        narration_intro: worldNarrationIntro,
        narration_outro: worldNarrationOutro
    };
    axios.post('http://127.0.0.1:8002/upsert_world/', updatedWorld)
      .then(res => console.log(res))
      .catch(err => console.log(err));
  };

  const saveScene = () => {
    // console.log('saving scene')
    // console.log('previousSceneName: ', previousSceneName)
    // const previousScene = scenes.find(scene => scene.scene_name === currentScene.previous_scene);
    const previousScene = scenes.find(scene => scene.scene_name === previousSceneName)
    // console.log('previousScene: ', previousScene)
    const previousSceneId = previousScene ? previousScene._id : '';
    // console.log('previouSceneId: ', previousSceneId)
    // console.log(currentScene)
    // console.log(sceneNpcName)
    // console.log(sceneNpcPrompt)
    const updatedScene = {
        ...currentScene,
        objectives: currentScene.objectives.map(objective => [...objective]),
        previous_scene: previousSceneId === '' ? null : previousSceneId,
        NPCs: sceneNPCs
        // NPCs: { sceneNpcName: {scene_npc_prompt: sceneNpcPrompt}}
        // NPCs: { 
        // ...currentScene.NPCs,
        // [sceneNpcName]: {
        //   ...currentScene.NPCs[sceneNpcName],
        //   scene_npc_prompt: sceneNpcPrompt
        // }}
      }
    axios.post('http://127.0.0.1:8002/update_scene/', updatedScene)
      .then(res => console.log(res))
      .catch(err => console.log(err));
  }

  const saveNpc = () => {
    const updatedNpc = {...currentNpc, personality: npcPersonality, knowledge: npcKnowledge}
    // console.log(updatedNpc)
    axios.post('http://127.0.0.1:8002/upsert_npc/',updatedNpc)
    .then(res=>console.log(res))
    .catch(err=>console.log(err))
  }

  const createNewScene = () => {
    // console.log('into CreateNewScene')
    const foundScene = scenes.find(scene => scene.scene_name === currentScene.previous_scene);
    const newScene = { 
      world_name: currentWorld.world_name, 
      scene_name: currentScene.scene_name, 
      previous_scene: foundScene ? foundScene._id : null,
      NPCs: { sceneNpcName: {scene_npc_prompt: sceneNpcPrompt}},
      // NPCs: {
      //   ...currentScene.NPCs,
      //   [sceneNpcName]: {
      //     ...currentScene.NPCs[sceneNpcName],
      //     scene_npc_prompt: sceneNpcPrompt
      //   }},
      objectives: currentScene.objectives,
      narration_intro: currentScene.narration_intro,
      narration_outro: currentScene.narration_outro,
      background_image_filepath: currentScene.background_image_filepath,
      music_filepath: currentScene.music_filepath
    };
    // console.log(newScene)
    axios.post('http://127.0.0.1:8002/insert_scene/', newScene)
      .then(res => {
        // console.log(res);
        setCurrentScene({
          scene_name: "",
          previous_scene: null,
          NPCs: {},
          objectives: [],
          narration_intro: "",
          narration_outro: "",
          background_image_filepath: "",
          music_filepath: ""
        });
        handleSceneEditor();
      })
      .catch(err => console.log(err));
  };

  const createNewNpc = () => {
    const newNpc = { world_name: currentWorld.world_name, npc_name: newNpcName, personality: newNpcPersonality };
    axios.post('http://127.0.0.1:8002/upsert_npc/', newNpc)
        .then(res => {
            // console.log(res);
            setNewNpcName('');
            setNewNpcPersonality('');
            // Optionally, refresh your list of NPCs here
            handleNpcEditor();
        })
        .catch(err => console.log(err));
  }

  // After picking a world you have to pick an Editor
  if (currentWorld._id && editorOption === null) {
    return (
      <div>
        <button onClick={() => setCurrentWorld({world_name: "",world_description: "",narration_intro: "",narration_outro: "",background_image_filepath: "",music_filepath: ""})}>Back</button>
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
              <textarea value={worldDescription} onChange={(e) => setWorldDescription(e.target.value)}></textarea>
            </div>
            <div className="input-group">
              <label>Narration Intro</label>
              <textarea value={worldNarrationIntro} onChange={(e) => setWorldNarrationIntro(e.target.value)}></textarea>
            </div>
            <div className="input-group">
              <label>Narration Outro</label>
              <textarea value={worldNarrationOutro} onChange={(e) => setWorldNarrationOutro(e.target.value)}></textarea>
            </div>
            <button className="update-button" onClick={saveWorldChanges}>Save Changes to World</button>
          </div>
        </div>
      );
  }

  // the scene editor
  if (editorOption === 'scene') {
    function handleObjectiveChange(listIndex, index, newValue) {
      const updatedObjectives = [...currentScene.objectives];
      updatedObjectives[listIndex][index] = newValue;
      setCurrentScene({ ...currentScene, objectives: updatedObjectives });
  }
  
  function removeObjective(listIndex, index) {
      const updatedObjectives = [...currentScene.objectives];
      updatedObjectives[listIndex].splice(index, 1);
      setCurrentScene({ ...currentScene, objectives: updatedObjectives });
  }
  
  function addNewObjective(listIndex) {
      const updatedObjectives = [...currentScene.objectives];
      updatedObjectives[listIndex].push("");
      setCurrentScene({ ...currentScene, objectives: updatedObjectives });
  }
  
  function addNewObjectiveSet() {
      const updatedObjectives = [...currentScene.objectives, []];
      setCurrentScene({ ...currentScene, objectives: updatedObjectives });
  }
  
    return (
        <div className="WorldCreator">
            <button onClick={() => {setEditorOption(null); clearCurrentScene()}}>Back</button>
            <h1>Select a Scene:</h1>
            {scenes.map((scene) => (
                <button key={scene._id} onClick={() => {
                    console.log(scenes)
                    const matchedScene = scenes.find(scene2 => scene2._id === scene.previous_scene);
                    console.log('matchedScene: ', matchedScene)
                    const previous_scene_name_from_id = matchedScene ? matchedScene.scene_name : '';
                    setCurrentScene({...scene, previous_scene: previous_scene_name_from_id});
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
                    previous_scene: null,
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
                                onChange={(e) => {
                                  setCurrentScene({ ...currentScene, previous_scene: e.target.value });
                                  setPreviousSceneName(e.target.value);}
                                }>
                                <option value="">Select previous scene</option>
                                {scenes.map((scene, index) => (
                                <option key={index} value={scene.scene_name}>{scene.scene_name}</option>
                                ))}
                            </select>
                    </div>
                    <div className="input-group">
                            <label>NPC Name</label>
                            <select 
                                value={currentScene.npc_name || 'Select NPC'} 
                                onChange={(e) => {
                                  setCurrentScene({ ...currentScene, npc_name: e.target.value });
                                  setSceneNpcName(e.target.value);}}>
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
                    {currentScene.objectives.map((objectiveList, listIndex) => (
                      <div key={`list-${listIndex}`}>
                          <h3>Objective Set {listIndex + 1}</h3>
                          {objectiveList.map((objective, index) => (
                              <div key={`objective-${listIndex}-${index}`} className="input-group">
                                  <label>Objective {index + 1}</label>
                                  <input
                                      type="text"
                                      value={objective}
                                      onChange={(e) => handleObjectiveChange(listIndex, index, e.target.value)}
                                  />
                                  <FontAwesomeIcon
                                      icon={faTrash}
                                      onClick={() => removeObjective(listIndex, index)}
                                  />
                              </div>
                          ))}
                          <button onClick={() => addNewObjective(listIndex)}>Add New Objective</button>
                      </div>
                    ))}
                    <button onClick={addNewObjectiveSet}>Add New Objective Set</button>
                    <div className="input-group">
                        <label>Narration Intro</label>
                        <textarea value={currentScene.narration_intro || ''} onChange={(e) => setCurrentScene({ ...currentScene, narration_intro: e.target.value })}></textarea>
                    </div>
                    <div className="input-group">
                        <label>Narration Outro</label>
                        <textarea value={currentScene.narration_outro || ''} onChange={(e) => setCurrentScene({ ...currentScene, narration_outro: e.target.value })}></textarea>
                    </div>
                    <div className="input-group">
                        <label>Background Image Filepath</label>
                        <SceneBackgroundImageFileSelector scene_id={currentScene._id} defaultFileName={currentScene.background_image_filepath}/>
                    </div>
                    <div className="input-group">
                        <label>Music Filepath</label>
                        <SceneMusicFileSelector scene_id={currentScene._id} defaultFileName={currentScene.music_filepath}/>
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
                                value={currentScene.npc_name || 'Select NPC'} 
                                onChange={(e) => {
                                  setCurrentScene({ ...currentScene, npc_name: e.target.value });
                                  setSceneNpcName(e.target.value);}}>
                                {/* <option value="">Select NPC</option> */}
                                {npcs.map((npc, index) => (
                                <option key={index} value={npc.npc_name}>{npc.npc_name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="input-group">
                            <label>Scene NPC Prompt</label>
                            <textarea value={sceneNpcPrompt} onChange={(e) => setSceneNpcPrompt(e.target.value)}></textarea>
                        </div>
                        {currentScene.objectives.map((objectiveList, listIndex) => (
                          <div key={`list-${listIndex}`}>
                              <h3>Objective Set {listIndex + 1}</h3>
                              {objectiveList.map((objective, index) => (
                                  <div key={`objective-${listIndex}-${index}`} className="input-group">
                                      <label>Objective {index + 1}</label>
                                      <input
                                          type="text"
                                          value={objective}
                                          onChange={(e) => handleObjectiveChange(listIndex, index, e.target.value)}
                                      />
                                      <FontAwesomeIcon
                                          icon={faTrash}
                                          onClick={() => removeObjective(listIndex, index)}
                                      />
                                  </div>
                              ))}
                              <button onClick={() => addNewObjective(listIndex)}>Add New Objective</button>
                          </div>
                        ))}
                        <button onClick={addNewObjectiveSet}>Add New Objective Set</button>
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
                <button key={npc._id} onClick={() => {
                  setCurrentNpc(npc);
                  setNpcPersonality(npc.personality !== undefined ? npc.personality : '');
                  setNpcKnowledge(npc.knowledge != undefined ? npc.knowledge : '')}}>
                {npc.npc_name}
                </button>
            ))}
            <button onClick={() => {
              setCurrentNpc(null);
              setNpcPersonality('');
              setNpcKnowledge('');
              }}>Create a new NPC</button>
            {currentNpc ? (
            <div>
                <h1>{currentNpc.npc_name}</h1>
                <div className="input-group">
                <label>Personality</label>
                <textarea value={npcPersonality} onChange={(e) => {setNpcPersonality(e.target.value)}}></textarea>
                </div>
                <div className="input-group">
                <label>Knowledge</label>
                <textarea value={npcKnowledge} onChange={(e) => {setNpcKnowledge(e.target.value)}}></textarea>
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
        <button key={world._id} onClick={() => {setCurrentWorld(world); setWorldDescription(world.world_description)}}>
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