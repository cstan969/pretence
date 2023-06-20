import json
from GameDesignerAI import GameDesignerAI
from config import EXTRACTOR_MODEL
import re, ast
from mongodb.mongo_fncs import upsert_npc
import pprint

# from langchain.langchain.chat_models.vicuna import ChatVicuna
# from langchain.langchain.chat_models import ChatOpenAI
# from langchain.langchain.llms import openai
# from langchain.langchain.llms import OpenAI

from VicunaLLM.VicunaLLM import VicunaLLM
from langchain.llms import OpenAI

#Wrapped around ChatModel
class Extractor():
    def __init__(self,world_name):
        self.world_name=world_name
        self.game_designer_ai = GameDesignerAI(world_name)
        self.temperature=0

        if EXTRACTOR_MODEL == "vicuna-13b-1.1":
            # self.chat_model=ChatVicuna()
            self.llm = VicunaLLM()
        elif EXTRACTOR_MODEL == "gpt-3.5-turbo":
            self.llm = OpenAI()
        elif EXTRACTOR_MODEL == "starcoder":
            self.llm = VicunaLLM()
        else:
            self.llm = VicunaLLM()
            # self.llm = StarcoderLLM()

    def _extract(self, extraction_prompt):
        temperature = 0
        # with open('generic_extractor_prompt.txt','r') as infile:
        #     generic_extractor_prompt = infile.read()
        generic_extractor_prompt = """your goal is to extract structured information from a conversation 
        between User and GameDesignerAI.  First I will give you the conversation, then I will ask you to
        extract the structured information.\n\n'''\n"""
        prompt = generic_extractor_prompt

        prompt += self.game_designer_ai.get_conversation()
        prompt += """\n\n'''\n"""

        prompt += extraction_prompt
        unparsed_response = self.llm._generate(prompts=[prompt],stop=['\n' + "User" + ':'])
        print(unparsed_response)
        response = unparsed_response.generations[0][0].text
        print('response from extraction: ', response)
        # response = self.game_designer_ai.message_game_designer_ai_and_get_response(user_message=prompt, save_conversation=False, temperature=temperature)
        return response
    
    def extract_npc(self, npc_name):
        def find_dictionary(document):
            pattern = r'{([^}]+)}'  # Regex pattern to match the dictionary content
            match = re.search(pattern, document, re.DOTALL)
            
            if match:
                dictionary_str = match.group(1)
                try:
                    dictionary = ast.literal_eval('{' + dictionary_str + '}')
                    return dictionary
                except SyntaxError:
                    pass  # Ignore if the dictionary is not valid
            
            return None
        
        temperature = 0
        prompt = """Could you please extract information for """ + npc_name + """ in the JSON format below. 
        The value of agent prompt should be the prompt you would give to a generative AI in order to have it act as said NPC agent.  
        Your response should be of the json format below
        {
            'name': 'name',
            'physical description': 'physical description',
            'personality': 'personality',
            'mood': 'mood',
            'quest name': 'quest name',
            'quest objectives': 'quest objectives',
            'agent prompt': 'agent prompt'
        }
        """
        extracted = self._extract(extraction_prompt=prompt)
        npc_info = find_dictionary(extracted)
        upsert_npc(world_name=self.world_name,npc_name=npc_info['name'],npc_metadata=npc_info)
        print('---------')
        print('---upserting new npc---')
        pprint.pprint(self.world_name)
        pprint.pprint(npc_name)
        pprint.pprint(npc_info)
        return npc_info

    def extract_all_npc_names(self):
        #first extract the npc_names
        # with open('prompts/extract_all_npc_names.txt','r') as infile:
        #     prompt = infile.read()
        prompt="""User: Please extract a list of unique character names that we explicitly discussed in the conversation above.  I want the output format to be a python list of strings where each string is a unique character that we explicitly discussed.  Output this in the format of [character1, character2] if there are two characters or [character_name1,character_name2,character_name3] if there are three characters so on and so forth.  Output the list only.  I want no additional text."""
        extracted = self._extract(extraction_prompt=prompt)
        print('extracted: ', extracted)
        match = re.search("\[.*?\]",extracted)
        if match:
            npc_names = ast.literal_eval(match.group(0))
        # else:
        #     prompt="""I received a response from a large language model that is not of the structured format that I need.
        #     Can you take a look at the text below, figure out what the character names are, and then output a list of character names in the format of [name1, name2] which is just a json list.  To reiterate, if there are two characters Bob and Carl then the result should be a list like [Bob,Carl]"""
        #     prompt += "\n\n The text I want you to extract character names from: \n'''''\n"
        #     # I want the names to be of json/python format meaning the resultant output should character names in between brackets as shown above.
        #     # Just return the list of characters, I do not want any additional text."""
        #     prompt+=extracted
        #     self.game_designer_ai.llm.prompt(prompt=prompt,stop=["\nGameDesignerAI"],temperature=self.temperature)
        return npc_names

    def extract_all_npcs(self):
        all_npc_names = self.extract_all_npc_names()
        print('exctracted_npc_names: ', all_npc_names)
        npcs = []
        for npc_name in all_npc_names:
            npc = self.extract_npc(npc_name)
            npcs.append(npc)
        return npcs

    def extract_all(self):
        '''runs all extractions'''
        npcs = self.extract_all_npcs()
        return {
            'npcs': npcs
        }

    

# #Wrapped around LLM
# class Extractor():

#     def __init__(self,world_name):
#         self.world_name = world_name
#         self.game_designer_ai = GameDesignerAI(world_name)
#         self.temperature=0

#     def _extract(self, extraction_prompt):
#         temperature = 0
#         with open('generic_extractor_prompt.txt','r') as infile:
#             generic_extractor_prompt = infile.read()
#         prompt = generic_extractor_prompt
#         prompt += extraction_prompt
#         prompt += " The conversation is shown below:"
#         prompt += "\n\'\'\'\'\'\n"
#         prompt += self.game_designer_ai.get_conversation()
#         # prompt += """\n\"\"\"\"\"\n"""
#         # prompt += extraction_prompt
#         response=self.game_designer_ai.llm.prompt(prompt=prompt,stop=['\n' + "User" + ':'],temperature=temperature)
#         # response = self.game_designer_ai.message_game_designer_ai_and_get_response(user_message=prompt, save_conversation=False, temperature=temperature)
#         return response

#     def extract_npc(self, npc_name):
#         def find_dictionary(document):
#             pattern = r'{([^}]+)}'  # Regex pattern to match the dictionary content
#             match = re.search(pattern, document, re.DOTALL)
            
#             if match:
#                 dictionary_str = match.group(1)
#                 try:
#                     dictionary = ast.literal_eval('{' + dictionary_str + '}')
#                     return dictionary
#                 except SyntaxError:
#                     pass  # Ignore if the dictionary is not valid
            
#             return None
        
#         temperature = 0
#         prompt = """Could you please extract information for """ + npc_name + """ in the JSON format below. The value of agent prompt should be the prompt you would give to a generative AI in order to have it act as said NPC agent.  Your response should be of the json format below
#         {
#             'name': 'name',
#             'physical description': 'physical description',
#             'personality': 'personality',
#             'mood': 'mood',
#             'quest name': 'quest name',
#             'quest objectives': 'quest objectives',
#             'agent prompt': 'agent prompt'
#         }
#         """
#         extracted = self._extract(extraction_prompt=prompt)
#         npc_info = find_dictionary(extracted)
#         upsert_npc(world_name=self.world_name,npc_name=npc_info['name'],npc_metadata=npc_info)
#         print('---------')
#         print('---upserting new npc---')
#         pprint.pprint(self.world_name)
#         pprint.pprint(npc_name)
#         pprint.pprint(npc_info)
#         return npc_info

#     def extract_all_npc_names(self):
#         #first extract the npc_names
#         # with open('prompts/extract_all_npc_names.txt','r') as infile:
#         #     prompt = infile.read()
#         prompt="""Could you please extract a list of unique character names that we have explicitly discussed from the conversation below.  I want the output format to be a python list of strings where each string is a unique character that we explicitly discussed.  Output this in the format of [character1, character2] if there are two characters or [character_name1,character_name2,character_name3] if there are three characters so on and so forth"""
#         extracted = self._extract(extraction_prompt=prompt)
#         match = re.search("\[.*?\]",extracted)
#         if match:
#             npc_names = ast.literal_eval(match.group(0))
#         else:
#             prompt="""I received a response from a large language model that is not of the structured format that I need.
#             Can you take a look at the text below, figure out what the character names are, and then output a list of character names in the format of [name1, name2] which is just a json list.  To reiterate, if there are two characters Bob and Carl then the result should be a list like [Bob,Carl]"""
#             prompt += "\n\n The text I want you to extract character names from: \n'''''\n"
#             # I want the names to be of json/python format meaning the resultant output should character names in between brackets as shown above.
#             # Just return the list of characters, I do not want any additional text."""
#             prompt+=extracted
#             self.game_designer_ai.llm.prompt(prompt=prompt,stop=[],temperature=self.temperature)
#         return npc_names

#     def extract_all_npcs(self):
#         all_npc_names = self.extract_all_npc_names()
#         print('exctracted_npc_names: ', all_npc_names)
#         npcs = []
#         for npc_name in all_npc_names:
#             npc = self.extract_npc(npc_name)
#             npcs.append(npc)
#         return npcs

#     def extract_all(self):
#         '''runs all extractions'''
#         npcs = self.extract_all_npcs()
#         return {
#             'npcs': npcs
#         }
        