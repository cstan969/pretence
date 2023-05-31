import React, { useState } from 'react';
import axios from 'axios';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';

const App = () => {
    const [conversation, setConversation] = useState([]);

    const sendMessage = (message) => {
        setConversation([...conversation, { message: message, isUser: true }]);

        axios.post('http://localhost:8001/message_npc_and_get_response', {
            npc_name: 'Captain Valeria',
            user_name: 'Carl',
            user_message: message
        }).then((res) => {
            setConversation([...conversation, { message: res.data.response, isUser: false }]);
        });
    };

    return (
        <div className='app'>
            <ChatWindow conversation={conversation} />
            <ChatInput onSend={sendMessage} />
        </div>
    );
};

export default App;