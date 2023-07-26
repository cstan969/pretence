
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const SceneBackgroundImageFileSelector = ({ scene_id, defaultFileName }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState(defaultFileName || 'No file selected');
  const [fileSelected, setFileSelected] = useState(false); // New state
  const fileInputRef = useRef(); // Create a ref

  useEffect(() => {
    if (selectedFile) {
      handleUpload();
    }
  }, [selectedFile]);


  const handleBackgroundImageFileChange = (event) => {
    console.log('handleFileChange');
    const file = event.target.files[0];
    setSelectedFile(file);
    setFileName(file?.name || 'No file selected'); 
    setFileSelected(!!file); 
    console.log('file: ', file);
  };

  const handleUpload = () => {
    console.log('handleUpload');
    console.log(scene_id);
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      axios
        .post(`http://127.0.0.1:8002/set_scene_background_image_filepath?scene_id=${scene_id}`, formData)
        .then((res) => {
          console.log(res);
        })
        .catch((err) => console.log(err));
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <input ref={fileInputRef} type="file" style={{ visibility: 'hidden', position: 'absolute' }} onChange={handleBackgroundImageFileChange} />
      {fileSelected ? ( // If a file has been selected
        <p>{fileName}</p> // Show the filename as text
      ) : (
        // If no file has been selected yet, show the readonly input with the default filename
        <input type="text" value={fileName} readOnly style={{ flexGrow: 1 }} />
      )}
      <button onClick={() => fileInputRef.current.click()}> {/* Use the ref here */}
        Browse
      </button>
    </div>
  );
};


export default SceneBackgroundImageFileSelector;