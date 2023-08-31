
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
    music_filepath: "",
    max_number_of_dialogue_exchanges: null
  });
  const [previousSceneName, setPreviousSceneName] = useState('')
  const [npcs, setNpcs] = useState([]);
  const [currentNpc, setCurrentNpc] = useState(null);
  const [npcPersonality, setNpcPersonality] = useState('');
  const [npcKnowledge, setNpcKnowledge] = useState('');
  const [npcSpeechPatterns, setNpcSpeechPatterns] = useState('');
  const [sceneNpcName, setSceneNpcName] = useState('');
  const [sceneNpcPrompt, setSceneNpcPrompt] = useState('');
  const sceneNPCs = {
    [sceneNpcName]: {
      scene_npc_prompt: sceneNpcPrompt
    }
  };
  
  const [newNpcName, setNewNpcName] = useState('');
  const [newNpcPersonality, setNewNpcPersonality] = useState('');
  const [selectedTag, setSelectedTag] = useState("");
  const [selectedLevel, setSelectedLevel] = useState(0);
  const [npcKnowledgeList, setNpcKnowledgeList] = useState({});
  const [isNewScene, setIsNewScene] = useState(true);

  //play game as user variables
  const [playGameWorld, setPlayGameWorld] = useState('')
  const [playGameUser, setPlayGameUser] = useState('')
  const [playTestSceneWorld, setPlayTestSceneWorld] = useState('')
  const [playTestSceneScene, setPlayTestSceneScene] = useState('')
  const [playTestScenes, setPlayTestScenes] = useState([])


  //knowledge stuffs
  const [knowledgeTags, setKnowledgeTags] = useState([]);
  //const [knowledges, setKnowledges] = useState([]);
  const [currentKnowledge, setCurrentKnowledge] = useState({});
  const [isNewKnowledge, setIsNewKnowledge] = useState(true);

  const clearCurrentScene = () => {
    setCurrentScene({
      scene_name: "",
      previous_scene_name: "",
      previous_scene: "",
      NPCs: {},
      objectives: [],
      narration_intro: "",
      narration_outro: "",
      background_image_filepath: "",
      music_filepath: "",
      max_number_of_dialogue_exchanges: null
    });
    setSceneNpcName("");
    setSceneNpcPrompt("");
  };

  useEffect(() => {
    updateWorlds();
    updateUsers();
}, []); // An empty dependency array

  // For operations that run every time currentScene changes:
  useEffect(() => {
      console.log('currentScene has changed: ', currentScene);
  }, [currentScene]); 

//   // For operations that run every time currentScene changes:
//   useEffect(() => {
//     console.log('currentKnowledge has changed: ', currentKnowledge);
// }, [currentKnowledge]); 


  const updateWorlds = () => {
    axios.get('http://127.0.0.1:8002/get_all_worlds')
      .then(res => {
        setWorlds(res.data.worlds);
      })
      .catch(err => console.log(err));
  };

  const updateUsers = () => {
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
    updateWorlds()
  };

  const createUser = () => {
    setUsers(prevUsers => [...prevUsers, {user_name: newUserName}]);
    setPlayGameUser(newUserName);
    setNewUserName('');
    setShowPopupNewUser(false);
    axios.post('http://127.0.0.1:8002/upsert_user', {'user_name': newUserName})
    updateUsers()
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
    updateKnowledge();
  };

  const handleKnowledgeEditor = () => {
    updateKnowledge();
    setEditorOption('knowledge')
  };

  const updateKnowledge = () => {
    if (currentWorld) {
      axios.post('http://127.0.0.1:8002/get_all_unique_knowledge_tags_for_world/', { world_name: currentWorld.world_name })  
        .then(res => {
          console.log(res);
          setKnowledgeTags(res.data);
        })
        .then(res => {
          console.log('knowledge tags: ', knowledgeTags);
        })
        .catch(err => console.log(err));
    }
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
    const previousScene = scenes.find(scene => scene.scene_name === previousSceneName)
    const updatedScene = {
        ...currentScene,
        objectives: currentScene.objectives.map(objective => [...objective]),
        previous_scene: currentScene.previous_scene,
        previous_scene_name: currentScene.previous_scene_name,
        NPCs: sceneNPCs
      }
    // Update the Scene
    axios.post('http://127.0.0.1:8002/update_scene/', updatedScene)
      .then(res => console.log(res))
      .catch(err => console.log(err));
    // Update 'scenes' variable by re-pulling the scenes
    axios.post('http://127.0.0.1:8002/get_all_scenes_in_order/', { world_name: currentWorld.world_name })
      .then(res => setScenes(res.data.scenes))
      .catch(err => console.log(err));
  }

  const saveNpc = () => {
    const updatedNpc = {...currentNpc,
      personality: npcPersonality,
      knowledge: npcKnowledge,
      speech_patterns: npcSpeechPatterns,
      knowledge_tag_levels: npcKnowledgeList
    }

    // console.log(updatedNpc)
    axios.post('http://127.0.0.1:8002/upsert_npc/',updatedNpc)
    .then(res=>console.log(res))
    .catch(err=>console.log(err))
  }

  const createNewScene = () => {
    const newScene = { 
      world_name: currentWorld.world_name, 
      scene_name: currentScene.scene_name, 
      previous_scene: currentScene.previous_Scene ? currentScene.previous_scene : null,
      previous_scene_name: currentScene.previous_scene_name ? currentScene.previous_scene_name : "",
      NPCs: { sceneNpcName: {scene_npc_prompt: sceneNpcPrompt}},
      objectives: currentScene.objectives,
      narration_intro: currentScene.narration_intro,
      narration_outro: currentScene.narration_outro,
      background_image_filepath: currentScene.background_image_filepath,
      music_filepath: currentScene.music_filepath,
      max_number_of_dialogue_exchanges: currentScene.max_number_of_dialogue_exchanges
    };
    console.log('newScene: ', newScene)
    // Upsert the new scene
    axios.post('http://127.0.0.1:8002/insert_scene/', newScene)
      .then(res => {
        clearCurrentScene();
        setCurrentScene(curScene => ({...curScene, scene_name: res.data.scene_name, previous_scene: res.data.previous_scene, previous_scene_name: res.data.previous_scene_name}));
      })
      .catch(err => console.log(err));
    // Get the new updated 'scenes' variable from DB
    axios.post('http://127.0.0.1:8002/get_all_scenes_in_order/', { world_name: currentWorld.world_name })
      .then(res => {
        setScenes(res.data.scenes);
      })
      .catch(err => console.log(err));
    
    // get scene editor to update (ulgy way w/e)
    setEditorOption('world');
    setEditorOption('scene');
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
        <button onClick={() => setCurrentWorld({world_name: "",world_description: "",narration_intro: "",narration_outro: "",background_image_filepath: "",music_filepath: "",max_number_of_dialogue_exchanges:null})}>Back</button>
        <h1>{currentWorld.world_name}</h1>
        <button onClick={() => setEditorOption('world')}>World Editor</button>
        <button onClick={handleSceneEditor}>Scene Editor</button>
        <button onClick={handleNpcEditor}>NPC Editor</button>
        <button onClick={handleKnowledgeEditor}>Knowledge Editor</button>
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
    function handleObjectiveChange(listIndex, index, key, newValue) {
      const updatedObjectives = [...currentScene.objectives];
      updatedObjectives[listIndex][index] = {...updatedObjectives[listIndex][index], [key]: newValue};
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
                    console.log('selected scene: ', scene)
                    const matchedScene = scenes.find(scene2 => scene2._id === scene.previous_scene);
                    console.log('matchedScene: ', matchedScene)
                    setCurrentScene({...scene, previous_scene: matchedScene ? matchedScene._id : null, previous_scene_name: matchedScene ? matchedScene.scene_name : ""});
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
                  narration_outro: "",
                  max_number_of_dialogue_exchanges: null
              });
              setSceneNpcName("")
              setSceneNpcPrompt("")
              setIsNewScene(true);
            }}>
                New Scene Template
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
                                value={currentScene.previous_scene_name || ''} 
                                onChange={(e) => {
                                  setCurrentScene({ ...currentScene, previous_scene_name: e.target.value });
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
                                <div className="objective-group">
                                  <div className="input-group">
                                    <label>Quest Objective</label>
                                      <textarea
                                          placeholder="Quest Objective"
                                          value={objective.objective || ''}
                                          onChange={(e) => handleObjectiveChange(listIndex, index, 'objective', e.target.value)}
                                      />
                                  </div>

                                  <div className="input-group">
                                      <label>User Facing Objective String</label>
                                      <textarea
                                          placeholder="User Facing Objective String"
                                          value={objective.user_facing_objective_string || ''}
                                          onChange={(e) => handleObjectiveChange(listIndex, index, 'user_facing_objective_string', e.target.value)}
                                      />
                                  </div>

                                  <div className="input-group">
                                    <label>Prompt Completed</label>
                                      <textarea
                                          placeholder="Prompt Completed"
                                          value={objective.prompt_completed || ''}
                                          onChange={(e) => handleObjectiveChange(listIndex, index, 'prompt_completed', e.target.value)}
                                      />
                                  </div>

                                  <div className="input-group">
                                    <label>Prompt Available</label>
                                      <textarea
                                          placeholder="Prompt Available"
                                          value={objective.prompt_available || ''}
                                          onChange={(e) => handleObjectiveChange(listIndex, index, 'prompt_available', e.target.value)}
                                      />
                                  </div>

                                  <div className="input-group">
                                    <label>Prompt Unavailable</label>
                                      <textarea
                                          placeholder="Prompt Unavailable"
                                          value={objective.prompt_unavailable || ''}
                                          onChange={(e) => handleObjectiveChange(listIndex, index, 'prompt_unavailable', e.target.value)}
                                      />
                                  </div>
                              </div>
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
                    <div className="input-group">
                        <label>Max Number of Dialogue Exchanges (number)</label>
                        <textarea value={currentScene.max_number_of_dialogue_exchanges || null} onChange={(e) => setCurrentScene({ ...currentScene, max_number_of_dialogue_exchanges: e.target.value })}></textarea>
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
                                value={currentScene.previous_scene_name || ''} 
                                onChange={(e) => setCurrentScene({ ...currentScene, previous_scene_name: e.target.value })}>
                                <option value="">Select previous scene</option>
                                {scenes.map((scene, index) => (
                                <option key={index} value={scene.scene_name}>{scene.scene_name}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <button onClick={createNewScene}>Create Scene</button>
                </div>
            )}
        </div>
    );
}

  if (editorOption === 'knowledge') {
    
    function setCurrentKnowledgeFromTag(input_tag){
      console.log('---hello---');
      let k = {
        tag: input_tag,
        knowledge_description: "",
        level0: "",
        level1: "",
        level2: "",
        level3: "",
        level4: "",
        level5: ""
      }
      axios.post('http://127.0.0.1:8002/get_knowledge/', {tag: input_tag, world_name: currentWorld.world_name})
      .then(res => {
        res.data.forEach(item => {
          const levelKey = `level${item.level}`;
          console.log('levelKey: ', levelKey)
          k[levelKey] = item.knowledge;
          k['knowledge_description']=item.knowledge_description;
          setCurrentKnowledge(k);
        });
      })
      .catch(err => console.log(err));
    }

    function createNewKnowledge(){
      //add the additional tag to the set of tags
      setKnowledgeTags([...knowledgeTags, currentKnowledge.tag]);
      setIsNewKnowledge(false);
    }

    function upsertKnowledgeToDB(){
      console.log(currentKnowledge);
      const knowledge = {
        world_name: currentWorld.world_name,
        tag: currentKnowledge.tag,
        knowledge_description: currentKnowledge.knowledge_description,
      }
      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:0,knowledge:currentKnowledge.level0})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));

      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:1,knowledge:currentKnowledge.level1})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));
      
      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:2,knowledge:currentKnowledge.level2})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));

      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:3,knowledge:currentKnowledge.level3})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));

      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:4,knowledge:currentKnowledge.level4})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));

      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:5,knowledge:currentKnowledge.level5})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));

      axios.post('http://127.0.0.1:8002/upsert_knowledge/', {...knowledge,level:0,knowledge:currentKnowledge.level0})
      .then(res => console.log(res.data))
     .catch(err => console.log(err));
    }

    return (
      <div className="WorldCreator">
        <button onClick={() => setEditorOption(null)}>Back</button>
        <h1>Select Knowledge to Update:</h1>
        <select onChange={event => {
          setCurrentKnowledgeFromTag(event.target.value);
          setIsNewKnowledge(false);
        }}>
        <option value="">Choose Knowledge</option>
        {knowledgeTags.map((tag, index) => (
            <option key={index} value={tag}>
            {tag}
            </option>
        ))}
        </select>

        <button onClick={() => {
              setCurrentKnowledge({
                  tag: "",
                  knowledge_description: "",
                  level0: "",
                  level1: "",
                  level2: "",
                  level3: "",
                  level4: "",
                  level5: ""
              });
              setIsNewKnowledge(true);
            }}>
                Clear Knowledge Template
        </button>
        
        {isNewKnowledge ? (
          <div>
            <div className="input-group">
            <label>Tag</label>
            <input type="text" value={currentKnowledge ? currentKnowledge.tag : ''} onChange={(e) => setCurrentKnowledge({...currentKnowledge, tag: e.target.value}) }/>
            </div>
            <button onClick={() => {createNewKnowledge()}}>Create New Tag</button>
          </div>
        ) : (
          // <div key={JSON.stringify(currentKnowledge)}>
          <div>
            <div className="input-group">
            <label>Tag</label>
            <input type="text" value={currentKnowledge.tag} readOnly onChange={(e) => setCurrentKnowledge({...currentKnowledge, tag: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Description</label>
            <textarea value={currentKnowledge.knowledge_description} onChange={(e) => setCurrentKnowledge({...currentKnowledge, knowledge_description: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Level0: Everyone knows. Period.</label>
            <textarea  value={currentKnowledge.level0} onChange={(e) => setCurrentKnowledge({...currentKnowledge, level0: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Level 1: Common Knowledge.</label>
            <textarea  value={currentKnowledge.level1} onChange={(e) => setCurrentKnowledge({...currentKnowledge, level1: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Level 2: Acquainted</label>
            <textarea  value={currentKnowledge.level2} onChange={(e) => setCurrentKnowledge({...currentKnowledge, level2: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Level 3: Knows pretty well</label>
            <textarea  value={currentKnowledge.level3} onChange={(e) => setCurrentKnowledge({...currentKnowledge, level3: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Level 4</label>
            <textarea  value={currentKnowledge.level4} onChange={(e) => setCurrentKnowledge({...currentKnowledge, level4: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Level 5</label>
            <textarea  value={currentKnowledge.level5} onChange={(e) => setCurrentKnowledge({...currentKnowledge, level5: e.target.value}) }/>
            </div>
            <button onClick={() => {upsertKnowledgeToDB()}}>Update Knowledge</button>
          </div>
        )}
      </div>
    )
  }

  if (editorOption === 'npc') {
    function TagDropdown({ tags, onChange, value }) {
      return (
        <select value={value} onChange={e => onChange(e.target.value)}>
          <option value="">Select a tag</option>
          {tags.map(tag => (
            <option key={tag} value={tag}>
              {tag}
            </option>
          ))}
        </select>
      );
    }

    function LevelDropdown({ levels, onChange, value }) {
      return (
        <select value={value} onChange={e => onChange(e.target.value)}>
          <option value="">Select a level</option>
          {levels.map(level => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      );
    }


    const addKnowledgeToNpc = () => {
      setNpcKnowledgeList(prevList => ({...prevList, [selectedTag]: selectedLevel}));
    }

    // State and logic for the TagSelector
    const handleTagChange = (index, newTag) => {
      const newSelectedTags = [...selectedTags];
      newSelectedTags[index] = newTag;
      setSelectedTags(newSelectedTags);
    };

    return (
        <div className="WorldCreator">
            <button onClick={() => setEditorOption(null)}>Back</button>
            <h1>Select an NPC:</h1>
            {npcs.map((npc) => (
                <button key={npc._id} onClick={
                  () => {
                  setCurrentNpc(npc);
                  setNpcPersonality(npc.personality !== undefined ? npc.personality : '');
                  setNpcKnowledge(npc.knowledge != undefined ? npc.knowledge : '');
                  setNpcSpeechPatterns(npc.speech_patterns !== undefined ? npc.speech_patterns : '')
                  setNpcKnowledgeList(npc.knowledge_tag_levels != undefined ? npc.knowledge_tag_levels : {});
                }
                }>

                {npc.npc_name}
                </button>
            ))}
            <button onClick={() => {
              setCurrentNpc(null);
              setNpcPersonality('');
              setNpcKnowledge('');
              setNpcSpeechPatterns('');
              }}>Create a new NPC</button>
            {currentNpc ? (
            <div>
                <h1>{currentNpc.npc_name}</h1>
                <div className="input-group">
                <label>Personality</label>
                <textarea value={npcPersonality} onChange={(e) => {setNpcPersonality(e.target.value)}}></textarea>
                </div>
                <div className="input-group">
                <label>Speech Patterns</label>
                <textarea value={npcSpeechPatterns} onChange={(e) => {setNpcSpeechPatterns(e.target.value)}}></textarea>
                </div>
                <div className="input-group">
                <label>Knowledge</label>
                <textarea value={npcKnowledge} onChange={(e) => {setNpcKnowledge(e.target.value)}}></textarea>
                </div>
                

                <div>
                  <TagDropdown 
                    tags={knowledgeTags}
                    value={selectedTag}
                    onChange={setSelectedTag}
                  />
                  <LevelDropdown
                    levels={[0, 1, 2, 3, 4, 5]}
                    value={selectedLevel}
                    onChange={setSelectedLevel}
                  />
                  <button onClick={addKnowledgeToNpc}>Add Knowledge to NPC</button>
                  <div>
                    {Object.entries(npcKnowledgeList).map(([tag, level]) => (
                    <div key={tag}>
                      Tag: {tag}, Level: {level}
                    </div>
                    ))}
                  </div>
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