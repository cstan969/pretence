from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from GameDesignerAI import GameDesignerAI


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
    
    
if __name__ == '__main__':
    uvicorn.run(app,host='127.0.0.1',port=8003)