import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './SupportChat.css';

const SupportChat = ({ onResponse }) => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! Send me a picture of any item, and I will mathematically compare it against our inventory database to see if we have it in stock.' }
  ]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const previewUrl = URL.createObjectURL(file);
    
    setMessages(prev => [...prev, { 
      sender: 'user', 
      text: 'Do you have this?', 
      image: previewUrl 
    }]);

    setLoading(true);

    const formData = new FormData();
    formData.append('image', file);

    try {
      // Direct connection to FastAPI
      const response = await axios.post('http://127.0.0.1:8000/api/chat', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessages(prev => [...prev, { sender: 'bot', text: response.data.reply }]);
      
      if (onResponse) {
        onResponse(response.data.predictions, previewUrl);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I am having trouble connecting to the visual search engine.' }]);
      console.error(err);
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="chat-window-integrated">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            <div className="bubble">
              {msg.image && <img src={msg.image} alt="query" className="chat-image" />}
              {msg.text && <p>{msg.text}</p>}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="bubble loading">Computing vector similarities...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <button className="upload-btn primary" onClick={() => fileInputRef.current?.click()}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
          Upload Image
        </button>
        <input 
          type="file" 
          accept="image/*" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleImageUpload} 
        />
      </div>
    </div>
  );
};

export default SupportChat;
