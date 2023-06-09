import json
from GameDesignerAI import GameDesignerAI
import re, ast
from mongodb.mongo_fncs import upsert_npc
import pprint


class Extractor():

    def __init__(self,world_name):
        self.world_name = world_name
        self.game_designer_ai = GameDesignerAI(world_name)

    def _extract(self, extraction_prompt):
        temperature = 0
        with open('generic_extractor_prompt.txt','r') as infile:
            generic_extractor_prompt = infile.read()
        prompt = generic_extractor_prompt
        prompt += "\n\'\'\'\'\'\n"
        prompt += self.game_designer_ai.get_conversation()
        prompt += """\n\"\"\"\"\"\n"""
        prompt += extraction_prompt
        response = self.game_designer_ai.message_game_designer_ai_and_get_response(user_message=prompt, save_conversation=False, temperature=temperature)
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
        prompt = """===
        User: Could you please extract information for """ + npc_name + """ in the JSON format below. The value of agent prompt should be the prompt you would give to a generative AI in order to have it act as said NPC agent.  Your response should be of the json format below
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
        with open('prompts/extract_all_npc_names.txt','r') as infile:
            prompt = infile.read()
        extracted = self._extract(extraction_prompt=prompt)
        match = re.search("\[.*?\]",extracted)
        if match:
            npc_names = ast.literal_eval(match.group(0))
        return npc_names

    def extract_all_npcs(self):
        all_npc_names = self.extract_all_npc_names()
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
        