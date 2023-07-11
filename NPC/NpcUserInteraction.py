import os
from VicunaLLM.VicunaLLM import VicunaLLM
from mongodb.mongo_fncs import get_npc
from config import NpcUserInteraction_model
from langchain.llms import OpenAI


DEBUGGING = False

class NpcUserInteraction():

    def __init__(self, world_name, npc_name, user_name):
        self.world_name=world_name
        self.npc_name=npc_name
        self.user_name = user_name

        if NpcUserInteraction_model == "vicuna-13b-1.1":
            self.llm = VicunaLLM()
        elif NpcUserInteraction_model == "gpt-3.5-turbo":
            print('using OpenAI Turbo')
            self.llm = OpenAI()
        else:
            self.llm = VicunaLLM()
        # self.llm = VicunaLLM()

        self.npc_info = get_npc(world_name,npc_name)
        self.conversation_path = os.path.join('npcs',self.npc_name,'conversation.txt')
        self.starter_prompt_path = os.path.join('npcs',self.npc_name,'starter_prompt.txt')

        
    def get_conversation(self):
        if os.path.exists(self.conversation_path):
            with open(self.conversation_path,'r') as infile:
                conversation=infile.read()
        else:
            os.makedirs(os.path.dirname(self.conversation_path), exist_ok=True)
            conversation = self.user_name + ": hello\n" + self.npc_name + ": hello"
        return conversation

    def message_npc_and_get_response(self, user_message):
        '''Assemble the prompt and query the NPC to get a response'''
        #First we have to get the prompt for the NPC agent
        prompt = self._get_prompt()
        print('prompt: ', prompt)
        #Add the message to the conversation stored as part of this class
        formatted_user_message = '\n' + self.user_name + ': ' + user_message + '\n' + self.npc_name + ': '
        prompt += formatted_user_message      
        unparsed_response=self.llm._generate(prompts=[prompt],stop=['\n' + self.user_name + ':'])
        print('unparsed_response: ', unparsed_response)
        npc_response = unparsed_response.generations[0][0].text
        print(npc_response)
        print('----')
        formatted_npc_response = '\n' + self.npc_name + ": " + npc_response.lstrip().rstrip()
        formatted_npc_response = npc_response.lstrip().rstrip()

        #Save this message to the conversation
        with open(self.conversation_path,'a') as infile:
            infile.write(formatted_user_message)
        #Save the NPC's response to the conversation
        with open(self.conversation_path,'a') as infile:
            infile.write(formatted_npc_response)
        return formatted_npc_response
    
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt(),
            self._load_npc_in_world_prompt(),
            self._load_starter_prompt(),
            "----------\nHere is the conversation so far.  Please continue in 3 or fewer sentences.\nCONVERSATION:\n",
            self.get_conversation()
        ]
        return '\n'.join([fnc for fnc in prompt_assembly_fncs_in_order])


    def _load_generic_npc_prompt(self):
        # generic_npc_prompt_path = os.path.join('npcs','generic_npc_prompt.txt')
        # with open(generic_npc_prompt_path,'r') as infile:
        #     generic_npc_prompt = infile.read()
        # generic_npc_prompt = """A chat between a player in a game ("[[USER_NAME]]") and an NPC quest giver ("[[AI_NAME]]") in a video game. 
        #   The NPC gives helpful, detailed, and polite answers to the human's questions.  The assistant is proactive in engaging with the player 
        #   and helps to guide the player in the world."""
        generic_npc_prompt = """ROLE: Act like an NPC in a video game."""
        # generic_npc_prompt = """ROLE: You are an NPC in a single player video game. Your role is to converse with the game player by continuing the conversation shown below.\n\n"""
        # generic_npc_prompt = generic_npc_prompt.replace('[[AI_NAME]]',self.npc_name).replace('[[USER_NAME]]',self.user_name)
        return generic_npc_prompt

    def _load_npc_in_world_prompt(self):
        return """GAME INFORMATION:  The game itself is an RPG where the player is the owner of a traveling pub.  Various NPCs approach the pub and talk with the player.  You are one of these NPCs.\n\n"""
    
    def _load_starter_prompt(self):
        # if os.path.exists(self.starter_prompt_path):
        #     with open(self.starter_prompt_path,'r') as infile:
        #         starter_prompt = infile.read()
        # else:
        #     starter_prompt=self.npc_info['agent prompt']
        if 'Prompt' in self.npc_info:
            starter_prompt = """Here is information pertaining to the NPC:\n""" + self.npc_info['Prompt']
        else:
            starter_prompt = """Here is information pertaining to the NPC:\n """ + str(self.npc_info)
        # starter_prompt = '  '.join([str(value) for key,value in self.npc_info.items() if key not in ["_id","npc_name","world_name","last_updated"]])
        return starter_prompt

    