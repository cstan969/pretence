EMOTIONS = ["drunk",
            "angry",
            "trusting",
            "motivated",
            "sad",
            "happy",
            "afraid",
            "compassionate"]

# class NpcInterpersonalEmotions(Enum):
#     DRUNK = 1
#     ANGRY = 1
#     AFRAID = 1
#     TRUSTING = 1
#     HAPPY = 1
#     MOTIVATED = 1
#     COMPASSIONATE = 1
#     SAD = 1


# class EmotionalState():
#     def __init__(self, emotion: NPCEmotion, relationship_emotion: NPCRelationshipEmotion):
#         self.emotion = emotion
#         self.relationship_emotion = relationship_emotion
#         # self.emotional_susceptibility = NPC.emotional_susceptibility

#     def get_emotion(self):
#         return self.emotion

#     def get_relationship_emotion(self):
#         return self.relationship_emotion

#     def set_emotion(self, emotion):
#         self.emotion = emotion

#     def set_relationship_emotion(self, relationship_emotion):
#         self.relationship_emotion = relationship_emotion


# class NPC():

#     def __init__(self, world_name, npc_name):
#         self.world_name=world_name
#         self.npc_name=npc_name
#         pass

#     def _load_npc(self):
#         '''load the NPC from the database'''


import json, os, pprint, math
from VicunaLLM.VicunaLLM import VicunaLLM
from mongodb.mongo_fncs import get_npc, get_latest_npc_emotional_state, get_formatted_conversational_chain, upsert_user_npc_interaction, get_world
from config import NpcUserInteraction_model
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI


DEBUGGING = False

class NpcUserInteraction():

    def __init__(self, world_name, npc_name, user_name):
        self.world_name=world_name
        self.npc_name=npc_name
        self.user_name = user_name
        # self.llm  = ChatOpenAI(model='gpt-3.5-turbo')
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

        formatted_conversation = get_formatted_conversational_chain(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name)
        print('formatted_conversation: ', formatted_conversation)

        #First we have to get the prompt for the NPC agent
        prompt = self._get_prompt()
        print('prompt: ', prompt)


        #Add the message to the conversation stored as part of this class
        formatted_user_message = '\n' + self.user_name + ': ' + user_message + '\n' + self.npc_name + ': '
        prompt += formatted_user_message      


        template = """Question: {question}
        Answer: Provide the answer to my question in JSON format where the keys are user_message, npc_response, and npc_emotional_response. \
            The emotional response should be a dict with keys [drunk, angry, trusting, motivated, sad, happy, afraid, compassionate]."""
    
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        print('---response---')
        print(response)
        response = json.loads(response)
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

        return formatted_npc_response
    
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt(),
            self._load_npc_in_world_prompt(),
            self._load_starter_prompt(),
            "----------\nHere is the conversation so far.\nCONVERSATION:\n",
            self.get_conversation()
        ]
        return '\n'.join([fnc for fnc in prompt_assembly_fncs_in_order])


    def _load_generic_npc_prompt(self):
        generic_npc_prompt = """ROLE: Act like an NPC, {npc_name}, in a video game.  I will be a player character and seek to achieve the quest objectives.""".format(npc_name=self.npc_name)
        # generic_npc_prompt = """ROLE: You are an NPC in a single player video game. Your role is to converse with the game player by continuing the conversation shown below.\n\n"""
        # generic_npc_prompt = generic_npc_prompt.replace('[[AI_NAME]]',self.npc_name).replace('[[USER_NAME]]',self.user_name)
        return generic_npc_prompt

    def _load_npc_in_world_prompt(self):
        world_json = get_world(world_name=self.world_name)[0]
        world_npc_prompt = world_json['world_npc_prompt']
        return """GAME INFORMATION: {world_npc_prompt}\n\n""".format(world_npc_prompt=world_json['world_npc_prompt'])
    
    def _load_starter_prompt(self):
        prompt_info = json.dumps({k: v for k,v in self.npc_info.items() if k in ['mood','personality','quest objectives']})
        starter_prompt = """Here is information pertaining to {npc_name}:\n""".format(npc_name=self.npc_name) + prompt_info
        return starter_prompt
    
