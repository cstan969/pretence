from enum import Enum, auto
from config import NPCBUILDER_MODEL
from VicunaLLM.VicunaLLM import VicunaLLM
from langchain.chat_models import ChatOpenAI
from langchain.llms.llamacpp import LlamaCpp
from langchain import PromptTemplate, LLMChain
import pprint
import json
from mongodb.mongo_fncs import upsert_npc



class NPC_Builder():

    def __init__(self, world_name):
        self.world_name = world_name
        # self.llm = llm=LlamaCpp(
        #     model_path="/home/carl/Pretence/llama.cpp/models/Wizard-Vicuna-30B-Uncensored.ggmlv3.q4_0.bin", 
        #     verbose=False,
        #     max_tokens=5000,
        #     n_ctx=1024,
        #     n_batch=256,
        #     n_gpu_layers=11
        # )
        self.llm = ChatOpenAI(model='gpt-3.5-turbo')
        
    def _prompt_create_character(self, npc_data=None):
        question = """I am creating a grim hope style video game.  Can you create a JSON NPC character for me?  Fill in each value field. I want the character to be of the following format...

{
'npc_name': string,
'age': int, 
'gender': string,
'nick_names': List[string],
'Roles',
'Appearance':{'face':string,'body':string,'garb':string},
'Homeland':string,
'Current location:'string,
'Favorite_locations':List[string],
'Family and Early Life':string,
'Personality': string,
'Beliefs and values':string,
'Skills and abilities':string,
'Key life events':string,
'Involvement in the world':string,
'Reputation and relationships':string,
'motivations':string,
'Personal goals':string,
'Quests':quests,
'Topics_of_interest',
'Hobbies',
'Dreams':string,
'Fears_and_insecurities':string,
'Strengths':string,
'Weaknesses':string,
'emotional susceptibility': {},
“Secrets”:[{“secret”:secret,”unlock_condition”:{“emotion”:emotion,”unlock_threshold”:threshold(7-10)}}]




emotional_susceptibility should include the following keys [drunk, angry, afraid, trusting, happy, motivated, compassionate, sad].  The values of emotional_susceptibility should be between 1 and 10 where 1 means the NPC is not susceptible to anger/drunkenness etc.


I want the secrets of the character to be things that the NPC would not share with the NPC unless the player's connection with the NPC via an emotion reaches a certain threshold value ranging from 5-10
I want the emotional_responses of the character to be how the NPC responds or begins to act in the scenario that one of the aforementioned responses reaches a certain threshold (6-10)

The quest(s) should be an interpersonal quest that can be resolved through communication.  
'Quests':[{'quest_name':name,'emotion':emotion,'objectives':[{'objective':interpersonal objective,'emotional_threshold':the increasing emotional value from 4-10 that is required for the NPC to share the reward information,'reward':something the npc is willing to share}]}]

'Secrets' should be of the format [{
      "fact": “secret”,
      "unlock_condition": {
        "emotion": "ANTAGONISTIC",
        "unlock_threshold": 1-10
      }
    }]

"""
        
        template = """Question: {question}
        Answer: Provide the JSON output to my question."""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt,llm=self.llm)
        # unparsed_response=self.llm._generate(prompts=[prompt])
        response = llm_chain.run(question)
        response = json.loads(response)
        response['world_name'] = self.world_name
        upsert_npc(world_name=self.world_name,npc_name=response['npc_name'],npc_metadata=response)
        pprint.pprint(response)
        return response


builder = NPC_Builder(world_name='TraumaGame')
builder._prompt_create_character()