import React, { useState } from 'react';

const ChatInput = ({ onSend }) => {
    const [message, setMessage] = useState('');

    const sendMessage = (e) => {
        e.preventDefault();

        if(message !== '') {
            onSend(message);
            setMessage('');
        }
    };

    return (
        <form className='chat-input' onSubmit={sendMessage}>
            <input
                type='text'
                placeholder='Type a message...'
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <button type='submit'>Send</button>
        </form>
    );
};

export default ChatInput;