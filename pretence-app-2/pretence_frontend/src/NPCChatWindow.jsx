import { useState } from 'react'
import './App.css'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator } from '@chatscope/chat-ui-kit-react';

// "Explain things like you would to a 10 year old learning how to code."
function NPCChatWindow(props) {
  const {user_name, world_name, npc_name} = props
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: 'outgoing',
      sender: "user"
    };

    const newMessages = [...messages, newMessage];
    
    setMessages(newMessages);

    // Initial system message to determine Bot functionality
    // How it responds, how it talks, etc.
    setIsTyping(true);
    console.log('run processMessage')
    await processMessage(newMessages);
  };

  async function processMessage(messages) { // messages is an array of messages
    let user_message = messages[messages.length - 1].message;

    var request_data = {
      "world_name": world_name,
      "npc_name": npc_name,
      "user_name": user_name,
      "user_message": user_message
    };

    console.log(user_message)
    console.log('user_name: ', user_name)
    console.log('world_name: ', world_name)
    console.log('npc_name: ', npc_name)
  
    try {
      const response = await fetch('http://127.0.0.1:8001/message_npc_and_get_response', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(request_data),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      const bot_response_str = await response.json();
      console.log('bot response: ', bot_response_str.response)
      setMessages([...messages, {
        message: bot_response_str.response,
        sender: "Bot"
        }]);
    }
    catch (error) {
      console.error('Error:', error);
    }
    finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="App">
      <div style={{ position:"relative", height: "800px", width: "700px"  }}>
        <MainContainer>
          <ChatContainer>       
            <MessageList 
              scrollBehavior="smooth" 
              typingIndicator={isTyping ? <TypingIndicator content="Bot is typing" /> : null}
            >
              {messages.map((message, i) => {
                console.log(message)
                return <Message key={i} model={message} />
              })}
            </MessageList>
            <MessageInput placeholder="Type message here" onSend={handleSend} />        
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  )
}

export default NPCChatWindow