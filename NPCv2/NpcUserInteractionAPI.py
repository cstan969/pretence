from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from NPCv2.NpcUserInteraction_v3_kg_agent import NpcUserInteraction
from MissionOutcomes.mission_outcomes import MissionOutcomes
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


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


@app.post("/get_conversation")
async def get_conversation(q: dict)->dict:
    world_name=q['world_name']
    npc_name = q['npc_name']
    user_name = q['user_name']
    user_interaction = NpcUserInteraction(world_name=world_name,npc_name=npc_name,user_name=user_name)
    conversation = user_interaction.get_conversation()
    return {"conversation": conversation}

@app.post("/message_npc_and_get_response")
async def message_npc_and_get_response(q: dict)->dict:
    world_name=q['world_name']
    scene_id=q['scene_id']
    npc_name = q['npc_name']
    user_name = q['user_name']
    user_message = q['user_message']
    user_interaction = NpcUserInteraction(world_name=world_name,scene_id=scene_id,npc_name=npc_name,user_name=user_name)
    response = await user_interaction.message_npc_and_get_response(user_message=user_message)        
    return response

@app.post('/send_npcs_on_mission')
async def send_npcs_on_mission(q: dict)->dict:
    world_name = q['world_name']
    npc_names = q['npc_names']
    user_name = q['user_name']
    mission_id = q['mission_id']
    mo = MissionOutcomes(
            world_name=world_name,
            user_name=user_name,
            mission_id=mission_id,
            npc_names=npc_names)
    return mo.get_mission_outcome_and_debriefing()



# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1', port=8001)
