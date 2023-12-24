import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const login = async () => {
    try {
      const loginResponse = await axios.post(
        'http://localhost:8080/api/login',
        { username, password },
        { withCredentials: true }
      );

      if (loginResponse.status === 200) {
        console.log('Login successful');
        setIsLoggedIn(true);
      } else {
        console.error('Login failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const register = async () => {
    try {
      const registerResponse = await axios.post(
        'http://localhost:8080/api/register',
        { username, password },
        { withCredentials: true }
      );

      if (registerResponse.status === 201) {
        console.log('Registration successful');
        setIsLoggedIn(true);
      } else {
        console.error('Registration failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const uploadPhoto = async () => {
    if (!selectedImage) {
      console.error('No image selected');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('image', selectedImage);

      const uploadResponse = await axios.post(
        'http://localhost:8080/api/photos',
        formData,
        { withCredentials: true }
      );

      if (uploadResponse.status === 201) {
        console.log('Photo uploaded successfully');
        setUploadSuccess(true);

        setTimeout(() => {
          setUploadSuccess(false);
        }, 3000);
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const displayPhotos = async () => {
    try {
      const imagesResponse = await axios.get(
        'http://localhost:8080/api/photos',
        { withCredentials: true }
      );
  
      console.log('Images Response:', imagesResponse);  // Thêm dòng này
  
      if (imagesResponse.status === 200) {
        setImages(imagesResponse.data);
      } else {
        console.error('Failed to fetch photos');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setSelectedImage(file);
    const previewImageUrl = URL.createObjectURL(file);
    setPreviewImage(previewImageUrl);
  };

  return (
    <div>
      {!isLoggedIn ? (
        <div>
          <label>
            Username:
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
          <label>
            Password:
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <button onClick={login}>Login</button>
          <button onClick={register}>Register</button>
        </div>
      ) : (
        <>
          <input type="file" accept="image/*" id="imageInput" onChange={handleImageChange} />
          {previewImage && <img src={previewImage} alt="Preview" style={{ maxWidth: '200px', margin: '10px' }} />}
          <button onClick={uploadPhoto}>Save Photo</button>
          <button onClick={displayPhotos}>Display Photos</button>
          {images.map((image, index) => (
            <img
              key={index}
              src={`http://localhost:8080${image.url}`}
              alt={`Image ${index}`}
              style={{ maxWidth: '200px', margin: '10px' }}
            />
          ))}
          {uploadSuccess && <div>Photo saved successfully!</div>}
        </>
      )}
    </div>
  );
};

export default App;
