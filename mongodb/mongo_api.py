from mongo_utils import query_collection, upsert_item, delete_items
from fastapi import FastAPI, File, UploadFile

import mongo_fncs as fncs
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import pprint
import shutil



app = FastAPI()
origins = [
    "http://localhost:5173",
    "localhost:5173",
    "http://127.0.0.1:5173",
    "127.0.0.1:5173",
    "http://localhost:5174",
    "localhost:5174",
    "http://127.0.0.1:5174",
    "127.0.0.1:5174"
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
    npc = fncs.upsert_npc(
        world_name=q['world_name'],
        npc_name=q['npc_name'],
        npc_metadata={k:v for k,v in q.items() if k not in ['world_name','npc_name']}
    )
    return npc

@app.post("/get_npcs_in_world")
async def get_npcs_in_world(q:dict):
    world_name = q['world_name']
    npcs = fncs.get_npcs_in_world(world_name=world_name)
    # # return {"npcs": [npc['npc_name'] for npc in npcs]}
    return npcs

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
    return fncs.upsert_world(world_name=q['world_name'],data={k:v for k,v in q.items() if k not in ['world_name']})

@app.get("/get_all_worlds")
async def get_all_worlds():
    worlds = fncs.get_all_worlds()
    # return {"worlds": [world['world_name'] for world in worlds]}
    return {"worlds": worlds}

@app.post("/get_world")
async def get_world(q: dict)->dict:
    world = fncs.get_world(q['world_name'])
    return world

@app.post("/upsert_user")
async def upsert_user(q:dict):
    return fncs.upsert_user(user_name=q['user_name'])

@app.get("/get_all_users")
async def get_all_users():
    users = fncs.get_all_users()
    return users
    # return {"users": [user['user_name'] for user in users]}

@app.get("/get_user")
async def get_user(user_name: str):
    user = fncs.get_user(user_name)
    return {"user": user}

@app.get("/get_progress_of_user_in_game")
async def get_progress_of_user_in_game(q: dict):
    world_name = q['world_name']
    user_name = q['user_name']
    scene_id = fncs.get_progress_of_user_in_game(world_name=world_name,user_name=user_name)
    return {"scene_id": scene_id}

@app.post("/get_scene")
async def get_scene(q: dict):
    scene_id=q['scene_id']
    scene = fncs.get_scene(scene_id=scene_id)
    return {"scene": scene}

@app.post("/update_scene")
async def update_scene(q: dict):
    upserted_item = fncs.update_scene(scene_id=q['_id'],scene_info={k:v for k,v in q.items() if k not in ['_id']})
    return upserted_item

@app.post("/insert_scene")
async def insert_scene(q: dict):
    scene = fncs.insert_scene(
        world_name=q['world_name'],
        scene_info={k:v for k,v in q.items() if k not in ['_id','world_name','previous_scene']},
        previous_scene=q['previous_scene']
    )
    return scene

@app.post("/set_scene_background_image_filepath")
async def set_scene_background_image_filepath(scene_id: str, file: UploadFile = File(...)):
    return fncs.set_scene_background_image_filepath(scene_id=scene_id,file=file)

@app.post("/set_scene_music_filepath")
async def set_scene_music_filepath(scene_id: str, file: UploadFile = File(...)):
    return fncs.set_scene_music_filepath(scene_id=scene_id,file=file)
    
@app.post("/get_all_scenes_in_order")
async def get_all_scenes_in_order(q: dict):
    scenes = fncs.get_all_scenes_in_order(world_name=q['world_name'])
    return {'scenes': scenes}

@app.post("/get_scene_objectives_status")
async def get_scene_objectives_status(q:dict):
    return fncs.get_scene_objectives_status(scene_id=q['scene_id'],user_name=q['user_name'])

@app.post("/get_all_knowledge_for_world")
def get_all_knowledge_for_world(q:dict):
    world_name=q['world_name']
    return fncs.get_all_knowledge_for_world(world_name=world_name)

@app.post("/get_knowledge")
def get_knowledge(q:dict):
    world_name=q['world_name']
    tag = q['tag'] if 'tag' in list(q) else None
    return fncs.get_knowledge(world_name=world_name,tag=tag)
    

@app.post("/get_all_unique_knowledge_tags_for_world")
def get_all_unique_knowledge_tags_for_world(q:dict):
    world_name=q['world_name']
    return fncs.get_all_unique_knowledge_tags_for_world(world_name=world_name)

@app.post("/upsert_knowledge")
def upsert_knowledge(q:dict):
    world_name = q['world_name']
    tag = q['tag']
    knowledge_description = q['knowledge_description']
    level = q['level']
    knowledge=q['knowledge']
    return fncs.upsert_knowledge(world_name=world_name,tag=tag,knowledge_description=knowledge_description, knowledge=knowledge,level=level)

@app.post("/get_all_missions_for_world")
def get_all_missions_for_world(q:dict):
    world_name = q['world_name']
    return fncs.get_all_missions_for_world(world_name=world_name)

@app.post("/get_mission")
def get_mission(q:dict):
    mission_id = q['mission_id']
    return fncs.get_mission(mission_id=mission_id)

@app.post("/upsert_mission")
def upsert_mission(q:dict):
    mission_name = q['mission_name']
    mission_briefing = q['mission_briefing']
    world_name=q['world_name']
    possible_outcomes = q['possible_outcomes']
    id_based_availability_logic = q['id_based_availability_logic'] if 'id_based_availability_logic' in list(q) else ""
    name_based_availability_logic = q['name_based_availability_logic'] if 'name_based_availability_logic' in list(q) else ""
    associated_knowledge_tags = q['associated_knowledge_tags'] if 'associated_knowledge_tags' in list(q) else []
    return fncs.upsert_mission(
        world_name=world_name,
        mission_name=mission_name,
        mission_briefing=mission_briefing,
        possible_outcomes=possible_outcomes,
        id_based_availability_logic=id_based_availability_logic,
        name_based_availability_logic=name_based_availability_logic,
        associated_knowledge_tags=associated_knowledge_tags
        )




#npc_objectives
@app.post("/create_npc_objective")
def create_npc_objective(q:dict):
    return fncs.create_npc_objective(world_name=q['world_name'],npc_name=q['npc_name'])

@app.post("/delete_npc_objective")
def delete_npc_objective(q:dict):
    return fncs.delete_npc_objective(npc_objective_id=q['npc_objective_id'])

@app.post("/update_npc_objective")
def update_npc_objective(q:dict):
    return fncs.update_npc_objective(
        npc_objective_id=q['npc_objective_id'],
        world_name=q['world_name'],
        npc_name=q['npc_name'],
        objective_name=q['objective_name'],
        objective_completion_string=q['objective_completion_string'],
        prompt_completed = q['prompt_completed'] if 'prompt_completed' in list(q) else "",
        prompt_available = q['prompt_available'] if 'prompt_available' in list(q) else "",
        prompt_unavailable = q['prompt_unavailable'] if 'prompt_unavailable' in list(q) else "",
        name_based_availability_logic= q['name_based_availability_logic'] if 'name_based_availability_logic' in list(q) else "",
        id_based_availability_logic= q['id_based_availability_logic'] if 'id_based_availability_logic' in list(q) else "",
        effects = q['effects'] if 'effects' in list(q) else []
    )

@app.post("/get_npc_objectives")
def get_npc_objectives(q:dict):
    return fncs.get_npc_objectives(world_name=q['world_name'],npc_name=q['npc_name'])


@app.post("/get_available_companions")
def get_available_companions(q:dict):
    return fncs.get_available_companions(world_name=q['world_name'],user_name=q['user_name'])

@app.post("/get_available_missions")
def get_available_missions(q:dict):
    return fncs.get_available_missions(world_name=q['world_name'],user_name=q['user_name'])


@app.post("/get_completed_missions")
def get_completed_missions(q:dict):
    return fncs.get_completed_missions(world_name=q['world_name'], user_name=q['user_name'])


@app.post("/get_available_npcs")
def get_available_npcs(q:dict):
    return fncs.get_available_npcs(world_name=q['world_name'],user_name=q['user_name'])

@app.post("/convert_availability_logic_from_name_to_id")
def convert_availability_logic_from_name_to_id(q:dict):
    world_name = q['world_name']
    expr = q['expr']
    return {
        'id_based_availability_logic': fncs.convert_availability_logic_from_name_to_id(world_name=world_name,expr=expr)
    }

@app.post("/convert_availability_logic_from_id_to_name")
def convert_availability_logic_from_id_to_name(q:dict):
    expr = q['expr']
    return {
        'name_based_availability_logic': fncs.convert_availability_logic_from_id_to_name(expr=expr)
    }
    



################################
#####MULTI COLLECTION CALLS#####
#####ALSO SORT OF RENPY STUAFF##
################################

# @app.post("/reset_game_for_user")
# async def reset_game_for_user(q:dict):
#     return fncs.reset_game_for_user(world_name=q['world_name'],user_name=q['user_name'])

# @app.post("/set_renpy_init_state")
# async def set_renpy_init_state(q:dict)->dict:
#     return fncs.set_renpy_init_state(world_name=q['world_name'],user_name=q['user_name'])

@app.get("/get_renpy_init_state")
async def get_renpy_init_state()->dict:
    return fncs.get_renpy_init_state()

@app.post("/play_test_scene_in_renpy")
async def play_test_scene_in_renpy(q:dict):
    fncs.play_test_scene_in_renpy(world_name=q['world_name'],scene_id=q['scene_id'])

@app.post("/play_world_in_renpy")
async def play_world_in_renpy(q:dict):
    fncs.play_world_in_renpy(world_name=q['world_name'],user_name=q['user_name'])
