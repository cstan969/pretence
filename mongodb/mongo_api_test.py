from fastapi import FastAPI, HTTPException
from typing import Dict
import mongo_fncs as fncs



app = FastAPI()

@app.post("/upsert_npc")
async def upsert_npc(q: Dict[str, str]):
    try:
        fncs.upsert_npc(
            world_name=q['world_name'],
            npc_name=q['npc_name'],
            npc_metadata=q['npc_metadata']
        )
        return {"message": "NPC upserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_npcs_in_world")
async def get_npcs_in_world(world_name: str):
    try:
        npcs = fncs.get_npcs_in_world(world_name)
        return {"npcs": npcs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_npc")
async def get_npc(world_name: str, npc_name: str):
    try:
        npc = fncs.get_npc(world_name, npc_name)
        return {"npc": npc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_npc")
async def delete_npc(world_name: str, npc_name: str):
    try:
        fncs.delete_npc(world_name, npc_name)
        return {"message": "NPC deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upsert_world")
async def upsert_world(world_name: str):
    try:
        fncs.upsert_world(world_name)
        return {"message": "World upserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_all_worlds")
async def get_all_worlds():
    try:
        worlds = fncs.get_all_worlds()
        return {"worlds": worlds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_world")
async def get_world(world_name: str):
    try:
        world = fncs.get_world(world_name)
        return {"world": world}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upsert_user")
async def upsert_user(user_name: str):
    try:
        fncs.upsert_user(user_name)
        return {"message": "User upserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_all_users")
async def get_all_users():
    try:
        users = fncs.get_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_user")
async def get_user(user_name: str):
    try:
        user = fncs.get_user(user_name)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))