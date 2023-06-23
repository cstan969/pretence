import os
from VicunaLLM.VicunaLLM import VicunaLLM
from mongodb import mongo_fncs
import json
from config import GameDesigner_model
from langchain.llms import OpenAI

DEBUGGING = False

class GameDesignerAI():

    def __init__(self, world_name):
        self.user_name="User"
        self.world_name = world_name
        self.conversation_path = os.path.join('worlds',self.world_name,'game_designer_conversation.txt')
        
        if GameDesigner_model == "vicuna-13b-1.1":
            self.llm = VicunaLLM()
        elif GameDesigner_model == "gpt-3.5-turbo":
            print('using OpenAI Turbo')
            self.llm = OpenAI()
        else:
            self.llm = VicunaLLM()

    def get_conversation(self):
        if os.path.exists(self.conversation_path):
            with open(self.conversation_path,'r') as infile:
                conversation=infile.read()
        else:
            conversation=""
        return conversation

    def message_game_designer_ai_and_get_response(self, user_message, save_conversation=True,temperature=0):
        '''Assemble the prompt and query the Game Designer AI to get a response'''
        #First we have to get the prompt for Game Designer AI
        prompt = self._get_prompt()
        print('prompt: ', prompt)
        #Add the message to the conversation stored as part of this class
        formatted_user_message = '\n' + self.user_name + ': ' + user_message
        prompt += formatted_user_message
        # prompt += '\nGameDesignerAI: '

        #Save this message to the conversation in the file
        os.makedirs(os.path.dirname(self.conversation_path), exist_ok=True)
        

        unparsed_game_designer_ai_response=self.llm._generate(prompts=[prompt],stop=['\n' + self.user_name + ':'])
        print('unparsed_response: ', unparsed_game_designer_ai_response)

        game_designer_ai_response = unparsed_game_designer_ai_response.generations[0][0].text
        formatted_npc_response = '\n' + game_designer_ai_response.lstrip().rstrip()
        #Save this message to the conversation in the file
        if save_conversation:
            with open(self.conversation_path,'a') as infile:
                infile.write(formatted_user_message)
        if save_conversation:
            with open(self.conversation_path,'a') as infile:
                infile.write(formatted_npc_response)
        return game_designer_ai_response
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_game_designer_ai_prompt,
            self.get_conversation
        ]
        return '\n'.join([fnc() for fnc in prompt_assembly_fncs_in_order])

    def _load_generic_game_designer_ai_prompt(self):
        generic_npc_prompt_path = os.path.join('generic_game_designer_ai_prompt.txt')
        with open(generic_npc_prompt_path,'r') as infile:
            generic_npc_prompt = infile.read()
        generic_npc_prompt = generic_npc_prompt.replace('[[AI_NAME]]',"GameDesignerAI").replace('[[USER_NAME]]',self.user_name)
        return generic_npc_prompt
