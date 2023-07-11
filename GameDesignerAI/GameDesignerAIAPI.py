from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from GameDesignerAI import GameDesignerAI
from mongodb.mongo_fncs import upsert_npc, get_latest_npc_emotional_state

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
import pprint
import json



app = FastAPI()
origins = [
    "http://localhost:5173",
    "localhost:5173",
    "http://127.0.0.1:5173",
    "127.0.0.1:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

'''Given a world_name, message the game designer for that world_name and get a response.'''
@app.post("/message_game_designer_ai_and_get_response")
async def message_game_designer_ai_and_get_response(q:dict):
    world_name = q['world_name']
    user_message = q['user_message']
    gdai = GameDesignerAI(world_name=world_name)
    response = gdai.message_game_designer_ai_and_get_response(user_message=user_message)
    return {"response": response}

'''Given a world name, get the past conversation that has happened with the game designer AI for that world'''
@app.get('/get_conversation')
async def get_conversation(q:dict):
    world_name=q['world_name']
    gdai=GameDesignerAI(world_name=world_name)
    conversation = gdai.get_conversation()
    print('conversation inside api: ', conversation)
    return {"conversation": conversation}


@app.post('/build_npc_from_json')
async def build_npc_from_json(q:dict):
    def _summarize_character_json(character_json:dict):
        character_json = {k:v for k,v in character_json.items() if v != ''}
        llm = ChatOpenAI(model='gpt-3.5-turbo')
        template = """Question: {question}
        Answer: Provide the answer to my question."""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt,llm=llm)
        question="""I am creating a character in a video game.  Write a concise written/paragraph-form summary of the character as contained in the following JSON:  """ + json.dumps(character_json)
        print(question)
        response = llm_chain.run(question)
        print(response)
        return response
    
    character_json = q['character_json']
    del character_json['world_name']
    world_name=q['world_name']

    character_summary = _summarize_character_json(character_json)
    # character_summary = """The character in the video game is named Vegeta. He is known as the prince of the saijins. Vegeta has spikey yellow hair that sets him apart visually. In terms of personality, he is often portrayed as angry and feisty, always seeking out fights and challenges. His background is tragic, as his home planet was destroyed, resulting in the death of his entire family. This traumatic event fuels his motivations to become the strongest warrior. Vegeta possesses great strength, which is one of his prominent strengths in battles."""

    llm = ChatOpenAI(model='gpt-3.5-turbo')
    template = """Question: {question}
#     Answer: Provide the JSON output to my question."""
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt,llm=llm)
    q1 = """I am creating a video game character and could use some help completing the character.\n
        Here is the starting point of the character I want to make: {character_summary}. \
        Can you create a JSON representation of this character for me?  Fill in each field; I do not want any fields left empty. I want the character to be of the following format...\n""".format(character_summary=character_summary)
    q2 = """{
'npc_name': string,
'age': int, 
'gender': string,
'nick_names': List[string],
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
“Secrets”:[{“secret”:secret,”unlock_condition”:{“emotion”:emotion,”unlock_threshold”:threshold(7-10)}}],
"text-to-image prompt':string

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
    
'text-to-image prompt should be a prompt that I can use to describe the character to a text-to-image generator.  It should include gender, facial appearance, and clothing."""
    question = q1+q2
        
        
    


    response = llm_chain.run(question)
    response = json.loads(response)
    pprint.pprint(response)
    response['world_name'] = world_name
    upsert_npc(world_name=world_name,npc_name=response['npc_name'],npc_metadata=response)
    return {'character_info': response}
    
if __name__ == '__main__':
    uvicorn.run(app,host='127.0.0.1',port=8003)