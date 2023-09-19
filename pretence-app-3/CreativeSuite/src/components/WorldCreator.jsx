
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

  //NPC Stuffs
  const [npcs, setNpcs] = useState([]);
  const [currentNpc, setCurrentNpc] = useState(null);
  const [npcPersonality, setNpcPersonality] = useState('');
  const [npcKnowledge, setNpcKnowledge] = useState('');
  const [npcSpeechPatterns, setNpcSpeechPatterns] = useState('');
  const [npcObjectives, setNpcObjectives] = useState([]);
  const [newNpcName, setNewNpcName] = useState('');
  const [selectedTag, setSelectedTag] = useState("");
  const [selectedLevel, setSelectedLevel] = useState(0);
  const [npcKnowledgeList, setNpcKnowledgeList] = useState({});
  const [npcNameBasedAvailabilityLogic, setNpcNameBasedAvailabilityLogic] = useState("");
  const [npcIdBasedAvailabilityLogic, setNpcIdBasedAvailabilityLogic] = useState("");


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

  //Missions stuff
  const [currentMission, setCurrentMission] = useState({
    mission_name: "",
    mission_brief: "",
    possible_outcomes: [],
    name_based_availability_logic: "",
    id_based_availability_logic: ""
  });
  const [missions, setMissions] = useState([]);
  const [isNewMission, setIsNewMission] = useState(true);
  const [editingNpcsIndexes, setEditingNpcsIndexes] = useState(() => {
    return currentMission.possible_outcomes.map((outcome, index) => {
      return outcome.npcs.length > 0 ? index : null;
    }).filter(i => i !== null);
  });
  const [selectedNpcsForMission, setSelectedNpcsForMission] = useState([]);
  const [missionApiResponse, setMissionApiResponse] = useState("");


 

  useEffect(() => {
    updateWorlds();
    updateUsers();
}, []); // An empty dependency array

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

  const handleMissionEditor = () => {
    updateMissions();
    updateNpcs();
    setEditorOption('mission')
  };

  const updateMissions = () =>{
    if (currentWorld) {
      axios.post('http://127.0.0.1:8002/get_all_missions_for_world/', { world_name: currentWorld.world_name })  
        .then(res => {
          console.log(res);
          setMissions(res.data);
        })
        .then(res => {
          console.log('missions: ', missions);
        })
        .catch(err => console.log(err));
    }
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


  

  const createNewNpc = () => {
    const newNpc = { world_name: currentWorld.world_name, npc_name: newNpcName};
    axios.post('http://127.0.0.1:8002/upsert_npc/', newNpc)
        .then(res => {
            // console.log(res);
            setNewNpcName('');
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
        <button onClick={handleNpcEditor}>NPC Editor</button>
        <button onClick={handleKnowledgeEditor}>Knowledge Editor</button>
        <button onClick={handleMissionEditor}>Mission Editor</button>
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
            {/* <div className="input-group">
              <label>Narration Intro</label>
              <textarea value={worldNarrationIntro} onChange={(e) => setWorldNarrationIntro(e.target.value)}></textarea>
            </div>
            <div className="input-group">
              <label>Narration Outro</label>
              <textarea value={worldNarrationOutro} onChange={(e) => setWorldNarrationOutro(e.target.value)}></textarea>
            </div> */}
            <button className="update-button" onClick={saveWorldChanges}>Save Changes to World</button>
          </div>
        </div>
      );
  }

  if (editorOption === 'knowledge') {
    
    function setCurrentKnowledgeFromTag(input_tag){
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

  if (editorOption === 'mission'){

    const saveMission = () => {
      console.log('save mission: ', currentMission)
      axios.post('http://127.0.0.1:8002/upsert_mission/', {...currentMission,world_name:currentWorld.world_name})
      .then(res => console.log(res.data))
      .catch(err => console.log(err));
    };

    const createNewMission = () => {
      setIsNewMission(false);
    };

    const handleAddOutcome = () => {
      setCurrentMission(prevMission => ({
        ...prevMission,
        possible_outcomes: [...prevMission.possible_outcomes, {
          npcs: "",
          outcome_summary: "",
          outcome_name: "",
          effects: []
        }]
      }));
    }


    const sendNpcsOnMission = async () => {
      try {
        // Call your API endpoint using axios. Adjust the URL and payload as needed.
        const response = await axios.post('http://127.0.0.1:8001/send_npcs_on_mission/', 
        { world_name: currentWorld.world_name,
        npc_names: selectedNpcsForMission,
        mission_id: currentMission._id,
        user_name: 'James Thomas Stanhope'
        });
        setMissionApiResponse(JSON.stringify(response.data, null, 2));
      } catch (error) {
        console.error('Error sending NPCs on mission:', error);
        setMissionApiResponse("Failed to send NPCs on mission.");
      }
    };

    const handleOutcomeChange = (index, key, value) => {
      const newOutcomes = [...currentMission.possible_outcomes];
      newOutcomes[index][key] = value;
      setCurrentMission({
        ...currentMission,
        possible_outcomes: newOutcomes
      });
    }

    const toggleEditNpcs = (index) => {
      if (editingNpcsIndexes.includes(index)) {
        // If already in editing mode, toggle off and clear NPCs for this outcome
        setEditingNpcsIndexes(prevIndexes => prevIndexes.filter(i => i !== index));
        setCurrentMission(prevMission => {
          const updatedMission = {...prevMission};
          updatedMission.possible_outcomes[index].npcs = [];
          return updatedMission;
        });
      } else {
        // If not in editing mode, just toggle on
        setEditingNpcsIndexes(prevIndexes => [...prevIndexes, index]);
      }
    };

    const handleNpcSelectionChange = (index, selectedNpcs) => {
      const newOutcomes = [...currentMission.possible_outcomes];
      newOutcomes[index].npcs = selectedNpcs;
      setCurrentMission({
        ...currentMission,
        possible_outcomes: newOutcomes
      });
    }
  

    function updateMission(mission_id) {
      axios.post("http://127.0.0.1:8002/get_mission/", {mission_id: mission_id})
      .then(res => {
        setCurrentMission(res.data);
      })
      .catch(err => console.log(err))
      setIsNewMission(false);
    };

    const handleNameToIdLogicConversion = async () => {
      // If the name_based_availability_logic is empty, don't make the API call
      if (!currentMission.name_based_availability_logic.trim()) {
        setCurrentMission(prevState => ({
            ...prevState,
            id_based_availability_logic: ''
        }));
        return;
      }
    
      // Example API call
      axios.post("http://127.0.0.1:8002/convert_availability_logic_from_name_to_id", {'world_name': currentWorld.world_name,'expr': currentMission.name_based_availability_logic})
        .then(response => {
          console.log('Mission Updated:', response.data);
          setCurrentMission(prevState => ({
            ...prevState,
            id_based_availability_logic: response.data.id_based_availability_logic
          }));
        })
        .catch(err => {
          console.log('Error converting availability logic from name to id:', err);
        });
      };

    return(
      <div className="WorldCreator">
        <button onClick={() => setEditorOption(null)}>Back</button>

        <select onChange={event => {
          updateMission(event.target.value);
        }}>
        <option value="">Choose Mission</option>
        {missions.map((mission, index) => (
            <option key={mission._id} value={mission._id}>
            {mission.mission_name}
            </option>
        ))}
        </select>

        <button onClick={() => {
              setCurrentMission({
                mission_name: "",
                mission_briefing: "",
                possible_outcomes: [],
                name_based_availability_logic: "",
                id_based_availability_logic: ""
              });
              setIsNewMission(true);
            }}>
                Clear Mission Template
        </button>

        {!isNewMission ? (
          <div>
            <h3>Core</h3>
            <div className="input-group">
            <label>mission_name</label>
            <textarea readOnly value={currentMission.mission_name} onChange={(e) => setCurrentMission({...currentMission, mission_name: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>mission_briefing</label>
            <textarea value={currentMission.mission_briefing} onChange={(e) => setCurrentMission({...currentMission, mission_briefing: e.target.value}) }/>
            </div>
            <div className="input-group">
            <label>Name-Based Mission Availability Logic</label>
            <textarea value={currentMission.name_based_availability_logic} onChange={(e) => setCurrentMission({...currentMission, name_based_availability_logic: e.target.value}) }/>
            </div>
            <button onClick={handleNameToIdLogicConversion}>Convert to ID-based Logic</button>
            <div className="input-group">
            <label>(ReadOnly) ID-based Mission Availability Logic</label>
            <textarea readOnly value={currentMission.id_based_availability_logic} onChange={(e) => setCurrentMission({...currentMission, id_based_availability_logic: e.target.value}) }/>
            </div>

            <h3>Possible Outcomes</h3>
            {currentMission.possible_outcomes.map((outcome, index) => (
              <div key={index}>
                <button onClick={() => toggleEditNpcs(index)}>
                  Certain NPCs Only
                </button>

                {(editingNpcsIndexes.includes(index) || outcome.npcs.length > 0) && (
                  <div className="input-group">
                    <label>NPCs</label>
                    <select multiple value={outcome.npcs} onChange={(e) => handleNpcSelectionChange(index, Array.from(e.target.selectedOptions, option => option.value))}>
                      {npcs.map(npc => (
                        <option key={npc.npc_name} value={npc.npc_name}>
                          {npc.npc_name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                <div className="input-group">
                  <label>Outcome Name</label>
                  <input value={outcome.outcome_name} onChange={(e) => handleOutcomeChange(index, 'outcome_name', e.target.value)} />
                </div>
                <div className="input-group">
                  <label>Outcome Summary</label>
                  <input value={outcome.outcome_summary} onChange={(e) => handleOutcomeChange(index, 'outcome_summary', e.target.value)} />
                </div>
                {/* <div className="input-group">
                  <label>Effects</label>
                  <input value={outcome.effects} onChange={(e) => handleOutcomeChange(index, 'effects', e.target.value)} />
                </div> */}
              </div>
            ))}
            <button onClick={handleAddOutcome}>Add Outcome</button>
            <h3>Save Your Changes!</h3>
            <button onClick={saveMission}>Save Updates to Mission</button>
            <h3>Test Mission</h3>
            <select multiple value={selectedNpcsForMission} onChange={(e) => setSelectedNpcsForMission(Array.from(e.target.selectedOptions, option => option.value))}>
              {npcs.map(npc => (
                <option key={npc.npc_name} value={npc.npc_name}>
                  {npc.npc_name}
                </option>
              ))}
            </select>

            <button onClick={sendNpcsOnMission}>Send NPCs on Mission</button>

            <div className="input-group">
              <label>Mission API Response</label>
              <textarea readOnly value={missionApiResponse} />
            </div>
          </div>
        ) : (
          <div>
            <div className="input-group">
            <label>mission_name</label>
            <textarea value={currentMission.mission_name} onChange={(e) => setCurrentMission({...currentMission, mission_name: e.target.value}) }/>
            </div>
            <button onClick={createNewMission}>Create Mission</button>
          </div>
        )}
      </div>
    )
  }

  if (editorOption === 'npc') {

    const saveNpc = () => {
      console.log('inside saveNpc: objectives: ', npcObjectives)
      const { objectives, ...restOfCurrentNpc } = currentNpc;
      const updatedNpc = {...restOfCurrentNpc,
        personality: npcPersonality,
        knowledge: npcKnowledge,
        speech_patterns: npcSpeechPatterns,
        knowledge_tag_levels: npcKnowledgeList,
        id_based_availability_logic: npcIdBasedAvailabilityLogic,
        name_based_availability_logic: npcNameBasedAvailabilityLogic
      }
      console.log('save Npc: ', updatedNpc);
  
  
      axios.post('http://127.0.0.1:8002/upsert_npc/',updatedNpc)
      .then(res=>console.log(res))
      .catch(err=>console.log(err))
      updateObjectives(npcObjectives);
  
    }
  

    function updateObjectives(npcObjectives) {
      console.log('log npc objectives: ', npcObjectives);
      npcObjectives.forEach((objective) => {
        const payload = {
          npc_objective_id: objective._id,
          world_name: currentWorld.world_name,
          npc_name: currentNpc.npc_name,
          objective_name: objective.objective_name,
          objective_completion_string: objective.objective_completion_string,
          prompt_available: objective.prompt_available,
          prompt_completed: objective.prompt_completed,
          prompt_unavailable: objective.prompt_unavailable,
          id_based_availability_logic: objective.id_based_availability_logic,
          name_based_availability_logic: objective.name_based_availability_logic,
          effects: objective.effects
        };
    
        axios.post("http://127.0.0.1:8002/update_npc_objective", payload)
          .then(response => {
            console.log('Objective updated:', response.data);
          })
          .catch(err => {
            console.log('Error updating objective:', err);
          });
      });
    }

    function NpcObjectivesComponent(props) {
      // const { updateObjectives: updateObjectivesFromContext } = useContext(NpcContext);
      const [npcObjectives, setNpcObjectives] = useState(props.npcObjectives || []);

      const addEffectToObjective = (index) => {
        console.log('newObjectives inside addEffectToObjective: ', npcObjectives)
        const newNpcObjectives = [...npcObjectives];
        newNpcObjectives[index].effects.push({ type: '', data: '' });
        setNpcObjectives(newNpcObjectives);
      }
      
      const handleEffectChange = (objectiveIndex, effectIndex, key, value) => {
        const newNpcObjectives = [...npcObjectives];
        newNpcObjectives[objectiveIndex].effects[effectIndex][key] = value;
        setNpcObjectives(newNpcObjectives);
      }
  
      const deleteEffectFromObjective = (objectiveIndex, effectIndex) => {
        const newNpcObjectives = [...npcObjectives];
        newNpcObjectives[objectiveIndex].effects.splice(effectIndex, 1);
        setNpcObjectives(newNpcObjectives);
      }


      const handleInputChange = (index, key, value) => {
          const newNpcObjectives = [...npcObjectives];
          newNpcObjectives[index][key] = value;
          console.log('new npc objectives: ', newNpcObjectives)
          setNpcObjectives(newNpcObjectives);
          console.log('npc objectives: ', npcObjectives);
      };

      

      const addNewObjective = () => {
        axios.post("http://127.0.0.1:8002/create_npc_objective",{world_name: currentWorld.world_name, npc_name: currentNpc.npc_name})
        .then(res => {
          console.log(res.data);
          const _id = res.data._id;
          const newObjective = {
            "_id": _id,
            "objective_name": "",
            "objective_completion_string": "",
            "prompt_completed": "",
            "prompt_available": "",
            "prompt_unavailable": "",
            "name_based_availability_logic": "",
            "id_based_availability_logic": "",
            "effects": []
          };
          setNpcObjectives([...npcObjectives, newObjective]);
          console.log('inside addNewObjective, npcObjectives is: ', npcObjectives);
        })
        .catch(err => console.log(err));
        
     };

     const handleNameToIdLogicConversionForObjective = (index) => {
      axios.post("http://127.0.0.1:8002/convert_availability_logic_from_name_to_id", {'world_name': currentWorld.world_name,'expr': npcObjectives[index].name_based_availability_logic})
      .then(response => {
        handleInputChange(index, 'id_based_availability_logic', response.data.id_based_availability_logic);
      })
      .catch(err => {
        console.log('Error converting availability logic from name to id:', err);
      });
     };

     const deleteObjective = (index) => {
      const objectiveToDelete = npcObjectives[index];
  
      const newNpcObjectives = [...npcObjectives];
      newNpcObjectives.splice(index, 1);
      setNpcObjectives(newNpcObjectives);
  
      axios.post("http://127.0.0.1:8002/delete_npc_objective", {
          npc_objective_id: objectiveToDelete._id
      })
      .catch(err => console.log(err));
     };
  
      return (
          <div>
              {npcObjectives.map((objective, index) => (
                  <div key={objective._id} className="objective-container">
                      <div className="input-group">
                          <label>Objective Name</label>
                          <textarea 
                              value={objective.objective_name} 
                              onChange={(e) => handleInputChange(index, 'objective_name', e.target.value)}
                          />
                      </div>
  
                      <div className="input-group">
                          <label>Objective Completion String</label>
                          <textarea 
                              value={objective.objective_completion_string}
                              onChange={(e) => handleInputChange(index, 'objective_completion_string', e.target.value)}
                          />
                      </div>

                      <div className="input-group">
                        <label>Name-Based Objective Availability Logic</label>
                        <textarea 
                          value={objective.name_based_availability_logic} 
                          onChange={(e) => handleInputChange(index, 'name_based_availability_logic', e.target.value)}
                        />
                      </div>

                      <button onClick={() => handleNameToIdLogicConversionForObjective(index)}>Convert to ID-based Logic</button>

                      <div className="input-group">
                        <label>(ReadOnly) ID-based Objective Availability Logic</label>
                        <textarea 
                          readOnly 
                          value={objective.id_based_availability_logic} 
                          onChange={(e) => handleInputChange(index, 'id_based_availability_logic', e.target.value)}
                        />
                      </div>

  
                      <div className="input-group">
                          <label>Prompt Completed</label>
                          <textarea 
                              value={objective.prompt_completed} 
                              onChange={(e) => handleInputChange(index, 'prompt_completed', e.target.value)}
                          />
                      </div>
  
                      <div className="input-group">
                          <label>Prompt Available</label>
                          <textarea 
                              value={objective.prompt_available}
                              onChange={(e) => handleInputChange(index, 'prompt_available', e.target.value)}
                          />
                      </div>
  
                      <div className="input-group">
                          <label>Prompt Unavailable</label>
                          <textarea 
                              value={objective.prompt_unavailable}
                              onChange={(e) => handleInputChange(index, 'prompt_unavailable', e.target.value)}
                          />
                      </div>

                      {objective.effects.map((effect, effectIndex) => (
                        <div key={effectIndex} className="effect-container">
                          <select 
                            value={effect.type}
                            onChange={e => handleEffectChange(index, effectIndex, 'type', e.target.value)}
                          >
                            <option value="">Select effect type</option>
                            <option value="Gain NPC as Companion">Gain NPC as Companion</option>
                            <option value="Player Knowledge Acquisition">Player Knowledge Acquisition</option>
                          </select>
                          {effect.type === 'Gain NPC as Companion' && (
                            <select 
                              value={effect.npc}
                              onChange={e => handleEffectChange(index, effectIndex, 'npc', e.target.value)}
                            >
                              <option value="">Select an NPC</option>
                              {npcs.map(npc => (
                                <option value={npc.npc_name} key={npc.npc_name}>
                                  {npc.npc_name}
                                </option>
                              ))}
                            </select>
                          )}
                          {effect.type === 'Player Knowledge Acquisition' && (
                            <textarea
                              value={effect.data}
                              onChange={e => handleEffectChange(index, effectIndex, 'data', e.target.value)}
                              placeholder="Enter knowledge information"
                            />
                          )}
                          <button 
                            onClick={() => deleteEffectFromObjective(index, effectIndex)}
                            className="delete-effect-btn"
                          >
                            🗑️  {/* This is a trash can emoji, but you can also use an icon */}
                          </button>
                        </div>
                      ))}
                      <button onClick={() => addEffectToObjective(index)}>Add Objective On-Completion Effect</button>


                      <button onClick={() => deleteObjective(index)}>Delete Objective</button>
                      {index !== npcObjectives.length - 1 && <hr className="objective-divider" />}
                  </div>
              ))}
              <button onClick={addNewObjective}>Add New Objective</button>
          </div>
      );
  }
  

  

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

    function setNpc(npc) {
      setCurrentNpc(npc);
      setNpcPersonality(npc.personality !== undefined ? npc.personality : '');
      setNpcKnowledge(npc.knowledge != undefined ? npc.knowledge : '');
      setNpcSpeechPatterns(npc.speech_patterns !== undefined ? npc.speech_patterns : '')
      setNpcKnowledgeList(npc.knowledge_tag_levels != undefined ? npc.knowledge_tag_levels : {});
      setNpcNameBasedAvailabilityLogic(npc.name_based_availability_logic != undefined ? npc.name_based_availability_logic : "");
      setNpcIdBasedAvailabilityLogic(npc.id_based_availability_logic != undefined ? npc.id_based_availability_logic : "");
      axios.post('http://127.0.0.1:8002/get_npc_objectives',{'world_name': currentWorld.world_name,'npc_name':npc.npc_name})
      .then(res => {
        console.log(res.data);
        setNpcObjectives(res.data);
      })
      .catch(err => console.log(err));
    }

    const handleNameToIdLogicConversion = async () => {
      // If the name_based_availability_logic is empty, don't make the API call
      if (!npcNameBasedAvailabilityLogic.trim()) {
        setNpcIdBasedAvailabilityLogic("");
        return;
      }
    
      // Example API call
      axios.post("http://127.0.0.1:8002/convert_availability_logic_from_name_to_id", {'world_name': currentWorld.world_name,'expr': npcNameBasedAvailabilityLogic})
        .then(response => {
          console.log('Npc Updated:', response.data);
          setNpcIdBasedAvailabilityLogic(response.data.id_based_availability_logic);
        })
        .catch(err => {
          console.log('Error converting availability logic from name to id:', err);
        });
      };

    return (
        <div className="WorldCreator">
            <button onClick={() => setEditorOption(null)}>Back</button>
            <h1>Select an NPC:</h1>
            {npcs.map((npc) => (
                <button key={npc._id} onClick={
                  () => {
                    setNpc(npc);
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
                <h3>Core</h3>
                <div className="input-group">
                <label>Innate Personality / Traits</label>
                <textarea value={npcPersonality} onChange={(e) => {setNpcPersonality(e.target.value)}}></textarea>
                </div>
                <div className="input-group">
                <label>Name-Based NPC Availability Logic</label>
                <textarea value={npcNameBasedAvailabilityLogic} onChange={(e) => setNpcNameBasedAvailabilityLogic(e.target.value) }/>
                </div>
                <button onClick={handleNameToIdLogicConversion}>Convert to ID-based Logic</button>
                <div className="input-group">
                <label>(ReadOnly) ID-based NPC Availability Logic</label>
                <textarea readOnly value={npcIdBasedAvailabilityLogic}/>
                </div>
                {/* <div className="input-group">
                <label>Speech Patterns</label>
                <textarea value={npcSpeechPatterns} onChange={(e) => {setNpcSpeechPatterns(e.target.value)}}></textarea>
                </div> */}
                {/* <div className="input-group">
                <label>Knowledge</label>
                <textarea value={npcKnowledge} onChange={(e) => {setNpcKnowledge(e.target.value)}}></textarea>
                </div> */}

                <h3>NPC Objectives</h3>
                <NpcObjectivesComponent npcObjectives={npcObjectives} />

               
                <h3>Knowledge</h3>
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
                <h3>Saving Updates</h3>

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
}

export default WorldCreator;