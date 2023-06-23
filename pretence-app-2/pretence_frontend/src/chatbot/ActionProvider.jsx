

class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }
  
  async handle_user_msg(user_message) {
    console.log('the users message: ', user_message)
    var request_data = {
      "npc_name": 'Captain Valeria',
      "user_name": 'Carl',
      "user_message": user_message
    };

  
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
      this.updateChatbotState(bot_response_str.response);
    }
    catch (error) {
      console.error('Error:', error);
    }
  }
  
  updateChatbotState(message) {
    console.log('message: ', message)
    // NOTE: This function is set in the constructor, and is passed in
    // from the top level Chatbot component. The setState function here
    // actually manipulates the top level state of the Chatbot, so it's
    // important that we make sure that we preserve the previous state.
    this.setState(prevState => ({
      ...prevState,
      messages: [...prevState.messages, message]
    }));
  }
}

export default ActionProvider;