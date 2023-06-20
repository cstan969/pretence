from typing import Optional
from mongodb.mongo_utils import query_collection, upsert_item, delete_items
# from mongodb.mongo_utils import query_collection, upsert_item, delete_items

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