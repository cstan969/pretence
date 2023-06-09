import os
from VicunaLLM.VicunaLLM import VicunaLLM
from mongodb.mongo_fncs import get_npc

DEBUGGING = False

class VicunaNpcUserInteraction():

    def __init__(self, world_name, npc_name, user_name):
        self.world_name=world_name
        self.npc_name=npc_name
        self.user_name = user_name
        self.llm = VicunaLLM()
        self.npc_info = get_npc(world_name,npc_name)
        import pprint
        pprint.pprint(self.npc_info)
        self.conversation_path = os.path.join('npcs',self.npc_name,'conversation.txt')
        self.starter_prompt_path = os.path.join('npcs',self.npc_name,'starter_prompt.txt')

        
    def get_conversation(self):
        if os.path.exists(self.conversation_path):
            with open(self.conversation_path,'r') as infile:
                conversation=infile.read()
        else:
            os.makedirs(os.path.dirname(self.conversation_path))
            conversation = ""
        return conversation

    def message_npc_and_get_response(self, user_message):
        '''Assemble the prompt and query the NPC to get a response'''
        #First we have to get the prompt for the NPC agent
        prompt = self._get_prompt()
        print('prompt: ', prompt)
        #Add the message to the conversation stored as part of this class
        formatted_user_message = '\n' + self.user_name + ': ' + user_message 
        prompt += formatted_user_message
        prompt += "\n" + self.npc_name + ": "

        #Save this message to the conversation in the file
        with open(self.conversation_path,'a') as infile:
            infile.write(formatted_user_message)

        npc_response=self.llm(prompt=prompt,stop=['\n' + self.user_name + ':'])
        # print('npc_response:\n')
        print(npc_response)
        print('----')
        formatted_npc_response = '\n' + npc_response.lstrip().rstrip()
        #Save this message to the conversation in the file
        with open(self.conversation_path,'a') as infile:
            infile.write(formatted_npc_response)
        return npc_response
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt,
            self._load_starter_prompt,
            self.get_conversation
        ]
        return '\n'.join([fnc() for fnc in prompt_assembly_fncs_in_order])


    def _load_generic_npc_prompt(self):
        generic_npc_prompt_path = os.path.join('npcs','generic_npc_prompt.txt')
        with open(generic_npc_prompt_path,'r') as infile:
            generic_npc_prompt = infile.read()
        generic_npc_prompt = generic_npc_prompt.replace('[[AI_NAME]]',self.npc_name).replace('[[USER_NAME]]',self.user_name)
        return generic_npc_prompt

    
    def _load_starter_prompt(self):
        if os.path.exists(self.starter_prompt_path):
            with open(self.starter_prompt_path,'r') as infile:
                starter_prompt = infile.read()
        else:
            starter_prompt=self.npc_info['agent prompt']
        return starter_prompt

    # def _get_who_conversed_last(self):
    #     '''look through a conversation and return who conversed last'''
    #     user_index = self.conversation.find('[[USER_NAME]]:')
    #     npc_index = self.conversation.find('[[AI_NAME]]:')
    #     if user_index == -1 and npc_index == -1:
    #         return 'none'
    #     if user_index > npc_index:
    #         return 'user'
    #     elif npc_index > user_index:
    #         return 'npc'

    # def interactive_cli_conversation(self):
    #     conversation = self.get_conversation()
    #     print(conversation)
    #     who_conversed_last = self._get_who_conversed_last()
    #     print('who_convsered_last: ', who_conversed_last)
    #     if who_conversed_last == 'none':
    #         response = self.prompt_npc
    #     elif who_conversed_last == 'npc':
    #         user_input = input('[[USER_NAME]]:')
    #     elif who_conversed_last == 'user':
    #         response = self.prompt_npc
        
    