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
