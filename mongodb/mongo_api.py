from fastapi import FastAPI
from mongo_utils import query_collection, upsert_item, delete_items
import mongo_fncs as fncs
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import pprint



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


@app.post("/upsert_npc")
async def upsert_npc(q: dict):
    fncs.upsert_npc(
        world_name=q['world_name'],
        npc_name=q['npc_name'],
        npc_metadata=q['npc_metadata']
    )
    return {"message": "NPC upserted successfully"}

@app.post("/get_npcs_in_world")
async def get_npcs_in_world(q:dict):
    npcs = fncs.get_npcs_in_world(world_name=q['world_name'])
    return {"npcs": [npc['npc_name'] for npc in npcs]}

@app.get("/get_npc")
async def get_npc(world_name: str, npc_name: str):
    npc = fncs.get_npc(world_name, npc_name)
    return {"npc": npc}

@app.delete("/delete_npc")
async def delete_npc(world_name: str, npc_name: str):
    fncs.delete_npc(world_name, npc_name)
    return {"message": "NPC deleted successfully"}

@app.post("/upsert_world")
async def upsert_world(q:dict):
    fncs.upsert_world(world_name=q['world_name'])
    return {"message": "World upserted successfully"}

@app.get("/get_all_worlds")
async def get_all_worlds():
    worlds = fncs.get_all_worlds()
    return {"worlds": [world['world_name'] for world in worlds]}

@app.get("/get_world")
async def get_world(world_name: str):
    world = fncs.get_world(world_name)
    return {"world": world}

@app.post("/upsert_user")
async def upsert_user(q:dict):
    fncs.upsert_user(
        user_name=q['user_name'])
    return {"message": "User upserted successfully"}

@app.get("/get_all_users")
async def get_all_users():
    users = fncs.get_all_users()
    return {"users": [user['user_name'] for user in users]}

@app.get("/get_user")
async def get_user(user_name: str):
    user = fncs.get_user(user_name)
    return {"user": user}

# if __name__ == '__main__':
#     uvicorn.run(app,host='127.0.0.1', port=8002)