import React from 'react';
import ChatBubble from './ChatBubble';

const ChatWindow = ({ conversation }) => {
    return (
        <div className='chat-window'>
            {conversation.map((chat, index) =>
                <ChatBubble
                    key={index}
                    message={chat.message}
                    isUser={chat.isUser}
                />
            )}
        </div>
    );
};

export default ChatWindow;