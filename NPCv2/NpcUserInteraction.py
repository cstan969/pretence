EMOTIONS = ["drunk",
            "angry",
            "trusting",
            "motivated",
            "sad",
            "happy",
            "afraid",
            "compassionate"]


import json, os, pprint, math
# from VicunaLLM.VicunaLLM import VicunaLLM
from mongodb.mongo_fncs import (
    get_npc,
    get_latest_npc_emotional_state,
    get_formatted_conversational_chain,
    upsert_user_npc_interaction,
    get_world,
    get_scene,
    get_scene_objectives_completed,
    mark_objectives_completed,
    progress_user_to_next_scene
)
from config import NpcUserInteraction_model
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI


DEBUGGING = False

class NpcUserInteraction():

    def __init__(self, world_name:str, scene_id:str, npc_name:str, user_name:str):
        self.world_name=world_name
        self.scene_id=scene_id
        self.npc_name=npc_name
        self.user_name = user_name
        self.llm = ChatOpenAI(model='gpt-3.5-turbo')
        self.npc_info = get_npc(world_name,npc_name)

    def calculate_new_emotional_state(self, npc_emotional_response: dict):
        '''
        Sample input format:
        "npc_emotional_response": {
            "drunk": 0,
            "angry": 0,
            "trusting": 2,
            "motivated": 5,
            "sad": 0,
            "happy": 0,
            "afraid": 0,
            "compassionate": 0
        }'''
        initial_emotional_state = get_latest_npc_emotional_state(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name)
        if initial_emotional_state is None:
            initial_emotional_state = {e:0 for e in EMOTIONS}
        final_emotional_state = {}
        for emotion, value in npc_emotional_response.items():
            if value != 0:
                final_emotional_state[emotion] = initial_emotional_state[emotion] + npc_emotional_response[emotion] * self.npc_info['emotional_susceptibility'][emotion] / 10
            else:
                final_emotional_state[emotion] = max([initial_emotional_state[emotion] - 0.2,0])
        return final_emotional_state
        
    def get_conversation(self):
        convo = get_formatted_conversational_chain(world_name=self.world_name,npc_name=self.npc_name,user_name=self.user_name)
        if convo is None:
            return self.user_name + ": hello\n" + self.npc_name + ": hello"
        return convo

    def message_npc_and_get_response(self, user_message):
        '''Assemble the prompt and query the NPC to get a response'''
        #First we have to get the prompt for the NPC agent
        prompt = self._get_prompt()
        print('---')
        print('prompt: ', prompt)
        print('---')


        #Add the message to the conversation stored as part of this class
        formatted_user_message = '\n' + self.user_name + ': ' + user_message + '\n' + self.npc_name + ': '
        prompt += formatted_user_message      


        template = """Question: {question}
        Answer: Provide the answer to my question as a dict where the keys are user_message, npc_response, npc_emotional_response, and objectives_completed. \
            user_message should simply be the user's last message (string)
            npc_response should simply be the npc's response (string)
            npc_emotional_response should be a dict with keys [drunk, angry, trusting, motivated, sad, happy, afraid, compassionate] and values from 0-10 where 10 indicates a strong emotional response and 0 indicates no response.
            objectives_completed should be a dictionary of objectives as given in the question with values equal to either 'completed' or 'not_completed' depending on whether that objective has been completed.
            The entire output should simply be a JSON dict"""
    
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        print('---response---')
        response = json.loads(response)
        pprint.pprint(response)
        npc_response = response['npc_response']
        formatted_npc_response = npc_response
        print('formatted_npc_response:')
        print(formatted_npc_response)

        #Save interaction to DB
        upsert_user_npc_interaction(
            world_name=self.world_name,
            user_name=self.user_name,
            npc_name=self.npc_name,
            user_message=response['user_message'],
            npc_response=response['npc_response'],
            npc_emotional_response=response['npc_emotional_response'],
            # npc_emotional_state=final_emotional_state
            )
        # mark the objectives that've been completed.  The output is the DB item with full list of completed objectives from the database
        updated_item = mark_objectives_completed(objectives_completed=response['objectives_completed'],scene_id=self.scene_id,user_name=self.user_name)
        if all(val == 'completed' for val in updated_item['objectives_completed'].values()):
            #mark the scene as the current scene in the world that the user is on
            progress_user_to_next_scene(world_name=self.world_name,user_name=self.user_name)
            response['scene_completed'] = True
        else:
            response['scene_completed'] = False

        return response
    
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt(), #role of the NPC generically
            self._load_npc_in_scene_prompt(), # role of the NPC in the scene (objectives etc)
            self._load_scene_objectives(), # the objectives of the scene for the protagonist to meet
            self._load_npc_prompt(), # summarization of the NPC (personality etc)
            self._load_npc_in_world_prompt(), # role of the NPC in the world
            self._load_conversation_prompt(), # conversation of user with NPC
        ]
        return '\n\n'.join([fnc for fnc in prompt_assembly_fncs_in_order])


    def _load_generic_npc_prompt(self):
        generic_npc_prompt = """ROLE: Act like an NPC, {npc_name}, in a video game.  I will be a player character and seek to achieve the objectives.""".format(npc_name=self.npc_name)
        return generic_npc_prompt
    
    def _load_npc_in_scene_prompt(self):
        scene_json = get_scene(scene_id=self.scene_id)
        pprint.pprint(scene_json)
        try:
            return scene_json['NPCs'][self.npc_name]['scene_npc_prompt']
        except:
            return ""

    def _load_scene_objectives(self):
        try:
            scene_json = get_scene(scene_id=self.scene_id)
            prompt = "Here are the objectives the protagonist needs to complete:\n"
            prompt += str(scene_json['objectives'])
            return prompt
        except Exception as e:
            print('exception: ', str(e))
            return ""

    def _load_npc_in_world_prompt(self):
        world_json = get_world(world_name=self.world_name)[0]
        if 'world_npc_prompt' in world_json:
            world_npc_prompt = world_json['world_npc_prompt']
        elif 'world_description' in world_json:
            world_npc_prompt = world_json['world_description']
        else:
            world_npc_prompt = ""
        return """GAME INFORMATION: {world_npc_prompt}\n\n""".format(world_npc_prompt=world_npc_prompt)
    
    def _load_npc_prompt(self):
        prompt_info = json.dumps({k: v for k,v in self.npc_info.items() if k in ['personality','role']})
        starter_prompt = """Here is information pertaining to {npc_name}:\n""".format(npc_name=self.npc_name) + prompt_info
        return starter_prompt
    
    def _load_conversation_prompt(self):
        prompt = "----------\nHere is the conversation so far.\nCONVERSATION:\n"
        prompt += self.get_conversation()
        return prompt
    
    
