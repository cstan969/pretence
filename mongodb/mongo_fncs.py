from typing import Optional
from mongodb.mongo_utils import query_collection, upsert_item, delete_items, get_current_date_formatted_no_spaces, get_current_datetime_as_string
# from mongodb.mongo_utils import query_collection, upsert_item, delete_items
from datetime import datetime

#####USERS#####
def upsert_user(user_name:str):
    collection_name='users'
    item={
        'user_name':user_name,
        '_id': '-'.join([collection_name,user_name])
    }
    upsert_item(collection_name=collection_name,item=item)

def get_all_users():
    return query_collection(collection_name='users',query={})

def get_user(user_name:str):
    return query_collection(collection_name='users',query={'user_name':user_name})


#####WORLDS#####
def upsert_world(world_name:str):
    '''create a new world and name'''
    collection_name = 'worlds'
    item={
        'world_name':world_name,
        '_id': '-'.join([collection_name,world_name])
    }
    upsert_item(collection_name=collection_name,item=item)

def get_all_worlds():
    return query_collection(collection_name='worlds',query={})

def get_world(world_name:str):
    return query_collection(collection_name='worlds',query={'world_name':world_name})


#####NPCS#####
def upsert_npc(world_name:str, npc_name:str, npc_metadata:dict):
    collection_name = 'npcs'
    item = npc_metadata
    item['world_name']=world_name
    item['npc_name']=npc_name
    item['_id']='-'.join([collection_name,world_name,npc_name])
    print('upsert_npc: ')
    print(item)
    upsert_item(collection_name=collection_name,item=item)

def get_npcs_in_world(world_name):
    '''given a world_name get all of the NPCs in that world.'''
    return query_collection(collection_name='npcs',query={'world_name':world_name})

def get_npc(world_name:str, npc_name:str):
    items = query_collection(collection_name='npcs',query={'world_name': world_name, 'npc_name': npc_name})
    return items[0] if len(items) > 0 else {}

def delete_npc(world_name:str,npc_name:str):
    delete_items(collect_name='npcs',query={'world_name':world_name,'npc_name':npc_name})


#####USER_NPC_INTERACTIONS#####
def get_user_npc_interactions(world_name:str, user_name: str, npc_name:str)->list:
    return query_collection(collection_name='user_npc_interactions',query={'world_name':world_name,'user_name':user_name,'npc_name':npc_name})

def upsert_user_npc_interaction(
        world_name:str,
        user_name: str,
        npc_name: str,
        user_message: str,
        npc_response: str,
        npc_emotional_response: Optional[dict]=None,
        npc_emotional_state: Optional[dict]=None
        ):
    collection_name='user_npc_interactions'
    created_at = get_current_datetime_as_string()
    item = {
        '_id':'-'.join([collection_name,world_name,user_name,npc_name, created_at]),
        'world_name':world_name,
        'user_name':user_name,
        'npc_name':npc_name,
        'user_message':user_message,
        'npc_response':npc_response,
        'npc_emotional_response':npc_emotional_response,
        'npc_emotional_state':npc_emotional_state,
        'created_at': created_at
    }
    upsert_item(collection_name=collection_name,item=item)

def delete_all_user_npc_interactions(
    world_name:str,
    user_name: str,
    npc_name: str):
    delete_items(collect_name='user_npc_interactions',query={'world_name':world_name,'npc_name':npc_name,'user_name':user_name}) 

def get_latest_npc_emotional_state(
    world_name:str,
    user_name:str,
    npc_name:str
)->dict:
    interactions = query_collection(collection_name='user_npc_interactions',query={'world_name':world_name,'user_name':user_name,'npc_name':npc_name})
    if interactions == []:
        return None
    ordered_interactions = sorted(interactions, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"))
    if 'npc_emotional_state' not in ordered_interactions[-1]:
        return None
    return ordered_interactions[-1]['npc_emotional_state']

def get_formatted_conversational_chain(
    world_name: str,
    user_name: str,
    npc_name: str
)->str:
    interactions = query_collection(collection_name='user_npc_interactions',query={'world_name':world_name,'user_name':user_name,'npc_name':npc_name})
    if interactions == []:
        return None
    ordered_interactions = sorted(interactions, key=lambda x: datetime.strptime(x['created_at'], "%Y-%m-%d %H:%M:%S"))
    conversation_lines = [f"{user_name}: {msg['user_message']}\n{npc_name}: {msg['npc_response']}\n" for msg in ordered_interactions]
    return ''.join(conversation_lines).rstrip()


#####SCENES#####
def upsert_scene(world_name: str, scene_info: dict, previous_scene: Optional[str]=None):
    #find scene_id that is linked to previous_scene currently
    current_scene_hooked_up_to_previous_scene = query_collection(collection_name='scenes',query={'world_name':world_name,'previous_scene':previous_scene})
    #upsert the new scene
    upserted_scene = {k:v for k,v in scene_info.items()}
    scene_id = '-'.join(['scenes',world_name,get_current_date_formatted_no_spaces()])
    upserted_scene['_id'] = scene_id
    upserted_scene['world_name'] = world_name
    upserted_scene['previous_scene'] = previous_scene
    upsert_item(collection_name='scenes',item=upserted_scene)
    #hook up the old next scene to the newly upserted scene
    if len(current_scene_hooked_up_to_previous_scene) > 0:
        current_scene_hooked_up_to_previous_scene = current_scene_hooked_up_to_previous_scene[0]
        current_scene_hooked_up_to_previous_scene['previous_scene'] = scene_id
        upsert_item(collection_name='scenes',item=current_scene_hooked_up_to_previous_scene)
    return upserted_scene



def get_next_scene(scene_id: Optional[str]=None):
    scenes = query_collection(collection_name='scenes',query={'_id':scene_id})
    return None if len(scenes) == 0 else scenes[0]
    
def get_all_scenes_in_order(world_name: str):
    ''''Return all of the scenes for some world in order'''
    scenes = query_collection(collect_name='scenes',query={'world_name':world_name})
    if len(scenes) == 0:
        return []
    else:
        ordered_scenes = []
        scene_dict = {scene['_id']: scene for scene in scenes}

        current_scene = None
        while True:
            if current_scene is None:
                next_scene = next((scene for scene in scenes if scene['previous_scene'] is None), None)
            else:
                next_scene = scene_dict.get(current_scene['_id'], None)

            if next_scene is None:
                break

            ordered_scenes.append(next_scene)
            current_scene = next_scene
    return ordered_scenes

def delete_scene(id:str):
    delete_items(collect_name='scenes',query={'_id':id}) 
