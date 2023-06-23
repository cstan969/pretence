

import { createChatBotMessage } from "react-chatbot-kit";

const config = {
  initialMessages: [createChatBotMessage(`placeholder to import old conversations.`)],
  botName: 'AI Game Designer',
  customStyles: {
      botMessageBox: {
      backgroundColor: '#376B7E',
      },
      chatButton: {
      backgroundColor: '#376B7E',
      },
  },
}

export default config