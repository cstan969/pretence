# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import os

# app = FastAPI()

# DEBUGGING = False

# class Message(BaseModel):
#     user_message: str

        
# @app.get("/npc/{npc_name}/conversation")
# async def get_npc_conversation(npc_name: str, user_name: str):
#     try:
#         npc = VicunaNpcUserInteraction(npc_name=npc,user_name=user_name)
#         return {"conversation": npc.get_conversation()}
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="NPC not found")

# @app.post("/npc/{npc_name}/message")
# async def message_npc_and_get_response(npc_name: str, user_name: str, message: Message):
#     try:
#         npc = VicunaNpcUserInteraction(npc_name=npc_name, user_name=user_name)
#         response = npc.message_npc_and_get_response(message.user_message)
#         return {"response": response}
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="NPC not found")


from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from VicunaNpcUserInteraction import VicunaNpcUserInteraction
import uvicorn


app = FastAPI()


class GetConversation(BaseModel):
    npc_name: str
    user_name: str

class MessageNpcAndGetResponse(BaseModel):
    npc_name: str
    user_name: str
    user_message: str

@app.post("/get_conversation")
async def get_conversation(npc_user_interaction: GetConversation):
    user_interaction = VicunaNpcUserInteraction(npc_user_interaction.npc_name, npc_user_interaction.user_name)
    conversation = user_interaction.get_conversation()
    return {"conversation": conversation}

@app.post("/message_npc_and_get_response")
async def message_npc_and_get_response(npc_user_interaction: MessageNpcAndGetResponse):
    user_interaction = VicunaNpcUserInteraction(npc_user_interaction.npc_name, npc_user_interaction.user_name)
    response = user_interaction.message_npc_and_get_response(npc_user_interaction.user_message)
    return {"response": response}

if __name__ == '__main__':
    uvicorn.run(app,host='127.0.0.1', port=8001)
