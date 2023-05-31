import React from 'react';

const ChatBubble = ({ message, isUser }) => {
    const bubbleClass = isUser ? 'user-bubble' : 'npc-bubble';

    return (
        <div className={`chat-bubble ${bubbleClass}`}>
            <p>{message}</p>
        </div>
    );
};

export default ChatBubble;