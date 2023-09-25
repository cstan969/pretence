from fastapi import FastAPI
import aggregator_functions as fncs
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import pprint
import shutil

from config import API_CORS_ORIGINS

app = FastAPI()
origins = API_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/genMemoriesFromBackstoryAndStoreGameInitIndex")
async def genMemoriesFromBackstoryAndStoreGameInitIndex(q:dict):
    return fncs.genMemoriesFromBackstoryAndStoreGameInitIndex(
        world_name=q['world_name'],
        npc_name=q['npc_name'],
        backstory=q['backstory']
    )