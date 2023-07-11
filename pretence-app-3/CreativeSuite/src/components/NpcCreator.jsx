import React, { useState } from 'react';
import '../styles/NpcCreator.css';

const NpcCreator = () => {
  const initialJsonData = {
    world_name: '',
    world_description: '',
    npc_name: '',
    npc_description: '',
    Quests: ''
  };

  const [jsonData, setJsonData] = useState(initialJsonData);
  const [characterJSONrepresentation, setCharacterJSONrepresentation] = useState(null);

  const handleInputChange = (event, field) => {
    const { value } = event.target;

    // Update the corresponding field in the JSON data
    setJsonData(prevData => ({
      ...prevData,
      [field]: value
    }));
  };

  const handleUpsertUserCharacter = async () => {
    // Output the JSON data to the console
    console.log('jsonData: ', jsonData)
    const response = await fetch('http://127.0.0.1:8003/build_npc_from_json', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({'world_name': 'test','character_json':jsonData}),
      });
      
    if (!response.ok) {
      throw new Error('Network response was not ok.');
    }
    const bot_response_str = await response.json();
    console.log('bot_response_str: ', bot_response_str)
    setCharacterJSONrepresentation(bot_response_str)
  };

  const handleTalkToCharacter = () => {

  }

  const handleFormSubmit = event => {
    event.preventDefault(); // Prevent form submission
  };

  const renderField = (field, value) => {
    if (typeof value === 'object') {
      // If the field is an object, recursively render its fields
      return (
        <div key={field}>
          <h3>{field}</h3>
          {Object.entries(value).map(([subField, subValue]) =>
            renderField(`${field}.${subField}`, subValue)
          )}
        </div>
      );
    } else if (Array.isArray(value)) {
      // If the field is an array, render input fields for each array item
      return (
        <div key={field}>
          <h3>{field}</h3>
          {value.map((item, index) => (
            <div key={index}>
              <input
                type="text"
                value={item}
                className='FormFillBox'
                onChange={event => handleInputChange(event, `${field}[${index}]`)}
              />
            </div>
          ))}
        </div>
      );
    } else {
      // If the field is a simple value, render a form for it
      return (
        <div key={field}>
          <h3>{field}</h3>
          <form onSubmit={handleFormSubmit}>
            <input
              type="text"
              value={value}
              className='FormFillBox'
              onChange={event => handleInputChange(event, field)}
            />
          </form>
        </div>
      );
    }
  };

  return (
    <div className="container">
      <div className="left-panel">
        {Object.entries(jsonData).map(([field, value]) => renderField(field, value))}
        <button style={{ fontSize: '20px', padding: '20px 30px' }} onClick={handleUpsertUserCharacter}>Generate Character</button>
      </div>
      <div className="right-panel">
        <div className="json-representation">
          <h2>JSON Representation of the Character</h2>
          {characterJSONrepresentation && <pre>{JSON.stringify(characterJSONrepresentation, null, 2)}</pre>}
        </div>
        {/* <button style={{ fontSize: '20px', padding: '20px 30px' }} onClick={handleTalkToCharacter}>Talk To Character</button> */}
      </div>
    </div>
  );
};

export default NpcCreator;