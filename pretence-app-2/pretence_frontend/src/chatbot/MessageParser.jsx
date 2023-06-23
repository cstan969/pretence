// class MessageParser {
//   constructor(actionProvider) {
//     this.actionProvider = actionProvider;
//   }

//   parse(message) {
//     console.log('user_message in MessageParser: ', message)
//     this.actionProvider.handle_user_msg(message)
//   }
// }

// export default MessageParser

export default function MessageParser(messages) {
  return messages.map((message, index) => {
    const { role, content } = message;
    return {
      id: index,
      role,
      message: content,
    };
  });
}