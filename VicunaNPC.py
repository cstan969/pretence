import os
from VicunaLLM import VicunaLLM

DEBUGGING = False

class VicunaNPC():

    def __init__(self, npc_name):
        self.npc_name=npc_name
        self.llm = VicunaLLM()
        self.conversation_path = os.path.join('npcs',self.npc_name,'conversation.txt')
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt,
            self._load_starter_prompt,
            self.get_conversation
        ]
        self.prompt = '\n'.join([fnc() for fnc in prompt_assembly_fncs_in_order])
     
    def _load_generic_npc_prompt(self):
        generic_npc_prompt_path = os.path.join('npcs','generic_npc_prompt.txt')
        with open(generic_npc_prompt_path,'r') as infile:
            self.generic_npc_prompt = infile.read()
        if DEBUGGING:
            print('generic_npc_prompt: ', self.generic_npc_prompt)
        return self.generic_npc_prompt

    def get_conversation(self):
        with open(self.conversation_path,'r') as infile:
            self.conversation=infile.read()
        if DEBUGGING:
            print('conversation: ', self.conversation)
        return self.conversation
    
    def _load_starter_prompt(self):
        starter_prompt_path = os.path.join('npcs',self.npc_name,'starter_prompt.txt')
        with open(starter_prompt_path,'r') as infile:
            self.starter_prompt = infile.read()
        if DEBUGGING:
            print('starter_prompt:\n',self.starter_prompt)
        return self.starter_prompt
    
    def user_sends_message_to_npc(self, user_message):
        '''Assemble the prompt and query the NPC to get a response'''
        #Add the message to the conversation stored as part of this class
        self.conversation += '\n' + '[[USER_NAME]]: ' + user_message
        self.prompt += '\n' + '[[USER_NAME]]: ' + user_message
        #Save this message to the conversation in the file
        with open(self.conversation_path,'a') as infile:
            infile.write('\n' + '[[USER_NAME]]: ' + user_message)

        response=self.llm(prompt=self.prompt,stop=['[[USER_NAME]]:'])
        print('response: ', response)
        self.conversation += '\n' + '[[AI_NAME]]: ' + response
        self.prompt += '\n' + '[[AI_NAME]]: ' + response
        #Save this message to the conversation in the file
        with open(self.conversation_path,'a') as infile:
            infile.write('\n' + '[[AI_NAME]]: ' + response)
        return response

    def get_who_conversed_last(self):
        '''look through a conversation and return who conversed last'''
        user_index = self.conversation.find('[[USER_NAME]]:')
        npc_index = self.conversation.find('[[AI_NAME]]:')
        if user_index == -1 and npc_index == -1:
            return 'none'
        if user_index > npc_index:
            return 'user'
        elif npc_index > user_index:
            return 'npc'

    def interactive_cli_conversation(self):
        conversation = self.get_conversation()
        print(conversation)
        who_conversed_last = self.get_who_conversed_last()
        print('who_convsered_last: ', who_conversed_last)
        if who_conversed_last == 'none':
            response = self.prompt_npc
        elif who_conversed_last == 'npc':
            user_input = input('[[USER_NAME]]:')
        elif who_conversed_last == 'user':
            response = self.prompt_npc
        
        

    
    

npc = VicunaNPC(npc_name='Captain Valeria')
# npc.interactive_cli_conversation()
# conversation = npc.get_conversation()
# print(conversation)
# npc.python_conversation()
# npc._load_conversation
npc.user_sends_message_to_npc('hello')

