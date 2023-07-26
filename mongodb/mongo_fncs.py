from typing import Optional
from mongodb.mongo_utils import query_collection, upsert_item, delete_items, get_current_date_formatted_no_spaces, get_current_datetime_as_string
# from mongodb.mongo_utils import query_collection, upsert_item, delete_items
from datetime import datetime
import pprint
import os
import subprocess
import shutil
from config import RENPY_SH_PATH


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
def upsert_world(world_name:str, data: dict):
    '''create a new world and name'''
    collection_name = 'worlds'
    item = data
    item['world_name'] = world_name
    item['_id'] = '-'.join([collection_name,world_name])
    return upsert_item(collection_name=collection_name,item=item)

def get_all_worlds():
    return query_collection(collection_name='worlds',query={})

def get_world(world_name:str):
    print('world_name passed to get_world: ', world_name)
    worlds = query_collection(collection_name='worlds',query={'world_name':world_name})
    return None if worlds is None else worlds[0]


#####NPCS#####
def upsert_npc(world_name:str, npc_name:str, npc_metadata:dict):
    npc = get_npc(world_name=world_name, npc_name=npc_name)
    item = {} if npc is None else npc
    collection_name = 'npcs'
    for k,v in npc_metadata.items():
        item[k] = v
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
    return items[0] if len(items) > 0 else None

def delete_npc(world_name:str,npc_name:str):
    delete_items(collection_name='npcs',query={'world_name':world_name,'npc_name':npc_name})


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
    delete_items(collection_name='user_npc_interactions',query={'world_name':world_name,'npc_name':npc_name,'user_name':user_name}) 

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



################
#####SCENES#####
################
def insert_scene(world_name: str, scene_info: dict, previous_scene: Optional[str]=None):
    #find scene_id that is linked to previous_scene currently
    if previous_scene is not None and 'scenes-' not in previous_scene:
        previous_scene = query_collection(collection_name='scenes',query={'world_name':world_name,'scene_name':previous_scene})[0]['_id']
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

def update_scene(scene_id: str, scene_info:dict)->dict:
    current_scene = query_collection(collection_name='scenes',query={'_id':scene_id})
    if current_scene == []:
        return None
    else:
        item_to_upsert=current_scene[0]
        for k,v in scene_info.items():
            item_to_upsert[k] = v
        upsert_item(collection_name='scenes',item=item_to_upsert)
        return item_to_upsert
        
    
def get_scene(scene_id: str)->dict:
    scenes = query_collection(collection_name='scenes',query={'_id':scene_id})
    return None if len(scenes) == 0 else scenes[0]


def get_next_scene(scene_id: Optional[str]=None)->dict:
    scenes = query_collection(collection_name='scenes',query={'previous_scene':scene_id})
    return None if len(scenes) == 0 else scenes[0]
    
def get_all_scenes_in_order(world_name: str):
    ''''Return all of the scenes for some world in order'''
    scenes = query_collection(collection_name='scenes',query={'world_name':world_name})
    if len(scenes) == 0:
        return []
    else:
        previous_scene_dict = {scene['previous_scene']: scene for scene in scenes}
        ordered_scenes = [scene for scene in scenes if scene['previous_scene'] is None]
        cur_scene = ordered_scenes[0]['_id']
        while cur_scene in previous_scene_dict:
            ordered_scenes.append(previous_scene_dict[cur_scene])
            cur_scene = previous_scene_dict[cur_scene]['_id']
    return ordered_scenes

def get_starting_scene_of_world(world_name: str):
    '''returns the starting scene for some world'''
    scenes = get_all_scenes_in_order(world_name=world_name)
    print('scenes in order: ', scenes)
    return scenes[0] if len(scenes)>0 else None

def delete_scene(id:str):
    delete_items(collection_name='scenes',query={'_id':id}) 

def set_scene_background_image_filepath(scene_id: str, file):
    scene = get_scene(scene_id=scene_id)
    world_name = scene['world_name']
    renpy_path = os.path.join(os.getenv('PRETENCE_PATH'),'RenpyProjects','CallumTest','game')
    renpy_filepath = os.path.join(renpy_path,'images',world_name,file.filename)
    db_filepath = f"{world_name}/{file.filename}"
    os.makedirs(os.path.dirname(renpy_filepath),exist_ok=True)
    os.makedirs(os.path.dirname(db_filepath),exist_ok=True)
    print(renpy_filepath)
    print(db_filepath)
    with open(renpy_filepath,'wb') as f:
        shutil.copyfileobj(file.file, f)
    with open(db_filepath,'wb') as f:
        shutil.copyfileobj(file.file, f)
    scene['background_image_filepath'] = db_filepath
    upsert_item(collection_name='scenes',item=scene)

def set_scene_music_filepath(scene_id: str, file):
    scene = get_scene(scene_id=scene_id)
    world_name = scene['world_name']
    renpy_path = os.path.join(os.getenv('PRETENCE_PATH'),'RenpyProjects','CallumTest','game')
    renpy_filepath = os.path.join(renpy_path,'audio',world_name,file.filename)
    db_filepath = f"{world_name}/{file.filename}"
    print(renpy_filepath)
    print(db_filepath)
    os.makedirs(os.path.dirname(renpy_filepath),exist_ok=True)
    os.makedirs(os.path.dirname(db_filepath),exist_ok=True)
    with open(renpy_filepath,'wb') as f:
        shutil.copyfileobj(file.file, f)
    with open(db_filepath,'wb') as f:
        shutil.copyfileobj(file.file, f)
    scene['music_filepath'] = db_filepath
    upsert_item(collection_name='scenes',item=scene)


###################################
#####SCENE_OBJECTIVES_COMPLETED#####
####################################

def mark_objectives_completed(objectives_completed: dict, scene_id: str, user_name: str):
    id = '-'.join(['scene_objectives_completed',scene_id,user_name])
    world_name = query_collection(collection_name='scenes',query={'_id':scene_id})[0]['world_name']
    items = query_collection(collection_name='scene_objectives_completed', query={'_id': id})
    if items == []:
        scene_objectives = {objective: 'not_completed' for sublist in query_collection(collection_name='scenes',query={'_id': scene_id})[0]['objectives'] for objective in sublist}
    else:
        scene_objectives = items[0]['objectives_completed']
    for obj,comp in objectives_completed.items():
        if comp == "completed" and obj in list(scene_objectives):
            scene_objectives[obj]="completed"
    item_to_upsert = {
        '_id': id,
        'world_name': world_name,
        'scene_id': scene_id,
        'user_name': user_name,
        'objectives_completed': scene_objectives
    }
    upsert_item(collection_name='scene_objectives_completed',item=item_to_upsert)
    return item_to_upsert

def get_scene_objectives_completed(scene_id: str, user_name: str):
    items = query_collection(collection_name='scene_objectives_completed', query={'_id':'-'.join(['scene_objectives_completed',scene_id,user_name])})
    return None if len(items)==0 else items[0]['objectives_completed']

def get_scene_objectives_status(scene_id: str, user_name: str):
    objectives = get_scene(scene_id=scene_id)['objectives']
    print('objectives: ', objectives)
    completed_objectives = get_scene_objectives_completed(scene_id=scene_id,user_name=user_name)
    print('completed_objectives: ', completed_objectives)
    if completed_objectives is not None:
        objectives_completed = []
        objectives_available = []
        objectives_unavailable = []
        for index, objective_set in enumerate(objectives):
            print('objective_set: ', objective_set)
            if not all(completed_objectives.get(objective) == "completed" for objective in objective_set):
                objectives_available = objective_set
                objectives_unavailable = [obj for sublist in objectives[index:] for obj in sublist]
                objectives_completed.extend([obj for obj in objective_set if completed_objectives.get(obj) == "completed"])
                break
            else: #all objectives in set completed
                objectives_completed.extend(objective_set)
    else:
        objectives_completed = []
        objectives_available = objectives[0]
        objectives_unavailable = [obj for sublist in objectives[1:] for obj in sublist]
    return {'completed': objectives_completed,'available': objectives_available,'unavailable':objectives_unavailable}

def delete_user_scene_objectives(scene_id: str, user_name:str):
    delete_items(collection_name='scenes',query={'_id':'-'.join(['scene_objectives_completed',scene_id,user_name])}) 

#####################
#####GAME STATUS#####
#####################

def get_progress_of_user_in_game(world_name: str, user_name: str)->str:
    '''Returns the scene_id that a user is up to for some world'''
    print('world_name: ', world_name)
    print('user_name: ', user_name)
    items = query_collection(collection_name='progress_of_user_in_game',query={'world_name': world_name,'user_name':user_name})
    print(items)
    if len(items) > 0:
        return items[0]['scene_id']
    else:
        #return the first scene of the world
        starting_scene = get_starting_scene_of_world(world_name=world_name)
        print(starting_scene)
        if starting_scene is not None:
            return starting_scene['_id']
        else:
            return None
        
def progress_user_to_next_scene(world_name:str, user_name:str):
    '''Progresses the user to the next scene in the game in the DB'''
    scene_id = get_progress_of_user_in_game(world_name=world_name,user_name=user_name)
    next_scene = get_next_scene(scene_id=scene_id)
    next_scene_id = next_scene['_id']
    item_to_upsert = {
        '_id': '-'.join(['progress_of_user_in_game',world_name,user_name]),
        'world_name': world_name,
        'user_name': user_name,
        'scene_id': next_scene_id
    }
    upsert_item(collection_name='progress_of_user_in_game',item=item_to_upsert)

def set_scene_the_user_is_in(world_name: str, user_name: str, scene_id: str):
    item_to_upsert = {
        '_id': '-'.join(['progress_of_user_in_game',world_name,user_name]),
        'world_name': world_name,
        'user_name': user_name,
        'scene_id': scene_id
    }
    upsert_item(collection_name='progress_of_user_in_game',item=item_to_upsert)


################################
#####MULTI COLLECTION CALLS#####
#####ALSO SORT OF RENPY STUAFF##
################################

def reset_game_for_user(world_name: str, user_name: str):
    delete_items(collection_name='progress_of_user_in_game',query={'world_name':world_name,'user_name':user_name})
    delete_items(collection_name='scene_objectives_completed',query={'world_name':world_name,'user_name':user_name})
    delete_items(collection_name='user_npc_interactions',query={'world_name':world_name,'user_name':user_name})
    return

def set_renpy_init_state(world_name: str, user_name: str):
    item_to_upsert = {
        '_id': 'renpy_init_state',
        'world_name': world_name,
        'user_name': user_name
    }
    upsert_item(collection_name='renpy_init_state', item = item_to_upsert)


def get_renpy_init_state():
    items = query_collection(collection_name='renpy_init_state',query={'_id': 'renpy_init_state'})
    print(items)
    return None if items is None else items[0]

def play_test_scene_in_renpy(world_name: str, scene_id: str):
    user_name='James Thomas Stanhope'
    reset_game_for_user(world_name=world_name, user_name=user_name)
    set_renpy_init_state(world_name=world_name,user_name=user_name)
    set_scene_the_user_is_in(world_name=world_name,user_name=user_name,scene_id=scene_id)
    os.system('pkill renpy')
    os.system(RENPY_SH_PATH + " &")
    # subprocess.Popen(['pkill','renpy'])
    # subprocess.Popen([RENPY_SH_PATH])

def play_world_in_renpy(world_name: str, user_name: str):
    set_renpy_init_state(world_name=world_name,user_name=user_name)
    # subprocess.Popen(['pkill','renpy'])
    # subprocess.Popen([RENPY_SH_PATH])
    os.system('pkill renpy')
    os.system(RENPY_SH_PATH + " &")
