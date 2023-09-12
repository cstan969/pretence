from typing import Optional
from mongodb.mongo_utils import query_collection, upsert_item, delete_items, get_current_date_formatted_no_spaces, get_current_datetime_as_string
# from mongodb.mongo_utils import query_collection, upsert_item, delete_items
from datetime import datetime
import pprint
import os
import subprocess
import shutil
import regex as re
from fuzzywuzzy import fuzz
from config import RENPY_SH_PATH, KNOWLEDGE_STORE_PATH


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
    upsert_npc(world_name=world_name, npc_name='Narrator')
    return upsert_item(collection_name=collection_name,item=item)

def get_all_worlds():
    return query_collection(collection_name='worlds',query={})

def get_world(world_name:str):
    worlds = query_collection(collection_name='worlds',query={'world_name':world_name})
    return None if worlds is None else worlds[0]


#####NPC_OBJECTIVES#####
def add_availability_dependent_to_npc_objective(npc_objective_id:str, new_dependent_id: str)->dict:
    collection_name='npc_objectives'
    item = query_collection(collection_name=collection_name,query={'_id': npc_objective_id})[0]
    print(item)
    availability_dependents = item['availability_dependents']
    availability_dependents.append(new_dependent_id)
    item['availability_dependents'] = list(set(availability_dependents))
    return upsert_item(collection_name=collection_name,item=item)

def remove_availability_dependent_from_npc_objective(npc_objective_id: str, dependent_id: str) -> dict:
    collection_name = 'npc_objectives'
    item = query_collection(collection_name=collection_name, query={'_id': npc_objective_id})[0]
    availability_dependents = item['availability_dependents']
    
    # Removing the dependent from the list
    if dependent_id in availability_dependents:
        availability_dependents.remove(dependent_id)
    
    item['availability_dependents'] = availability_dependents
    return upsert_item(collection_name=collection_name, item=item)

def create_npc_objective(world_name: str, npc_name: str):
    collection_name = 'npc_objectives'
    item_to_upsert = {
        '_id':'-'.join([collection_name,world_name,npc_name,get_current_date_formatted_no_spaces()]),
        'world_name': world_name,
        'npc_name': npc_name,
    }
    return upsert_item(collection_name=collection_name,item=item_to_upsert)

def delete_npc_objective(npc_objective_id: str):
    npc_objective = query_collection(collection_name='npc_objectives',query={'_id':npc_objective_id})[0]
    if 'availability_dependencies' in npc_objective and len(npc_objective['availability_dependencies']) > 0:
        remove_availability_dependency_links(dependency_ids=npc_objective['availability_dependencies'],id=npc_objective_id)
    delete_items(collection_name='npc_objectives',query={'_id':npc_objective_id})


def update_npc_objective(
        npc_objective_id: str,
        world_name: str,
        npc_name: str,
        objective_name: str,
        objective_completion_string: str,
        prompt_completed: Optional[str]="",
        prompt_available: Optional[str]="",
        prompt_unavailable: Optional[str]="",
        id_based_availability_logic: Optional[str]="",
        name_based_availability_logic: Optional[str]=""
):
    collection_name = 'npc_objectives'
    current_items = query_collection(collection_name=collection_name, query={'_id': npc_objective_id})
    availability_dependents = []
    if len(current_items)==0 and 'availability_dependents' in list(current_items[0]):
        availability_dependents = current_items[0]['availability_dependents']
    availability_dependencies = [] if id_based_availability_logic in (None, "") else re.findall(r'\[(.*?)\]', id_based_availability_logic)
    if len(availability_dependencies) > 0:
        add_availability_dependency_links(dependency_ids=availability_dependencies, id=npc_objective_id)

    
    item_to_upsert = {
        '_id': npc_objective_id,
        'world_name': world_name,
        'npc_name': npc_name,
        'objective_name': objective_name,
        'objective_completion_string': objective_completion_string,
        'prompt_completed': prompt_completed,
        'prompt_available': prompt_available,
        'prompt_unavailable': prompt_unavailable,
        'name_based_availability_logic': name_based_availability_logic,
        'id_based_availability_logic': id_based_availability_logic,
        'availability_dependencies': availability_dependencies,
        'availability_dependents': availability_dependents
    }
    print('item to upsert: ', item_to_upsert)
    return upsert_item(collection_name=collection_name,item=item_to_upsert)

def get_npc_objectives(world_name: str, npc_name: str)->list:
    collection_name = 'npc_objectives'
    return query_collection(collection_name=collection_name,query={'world_name':world_name,'npc_name':npc_name})

def get_all_npc_objectives_in_world(world_name: str)->list:
    collection_name = 'npc_objectives'
    return query_collection(collection_name=collection_name,query={'world_name':world_name})

def get_npc_objective_id_from_objective_name(world_name: str, npc_name: str, objective_name: str)->str:
    items = query_collection(collection_name='npc_objectives',query={
        'world_name':world_name,
        'npc_name':npc_name,
        'objective_name':objective_name
    })
    return items[0]['_id'] if len(items) == 1 else None

def get_npc_objective(npc_objective_id: str)->dict:
    collection_name = 'npc_objectives'
    items = query_collection(collection_name=collection_name,query={'_id':npc_objective_id})
    return items[0] if len(items)==1 else None 


#####NPCS#####

def add_availability_dependent_to_npc(npc_id:str, new_dependent_id: str)->dict:
    collection_name='npcs'
    item = query_collection(collection_name=collection_name,query={'_id': npc_id})[0]
    availability_dependents = item['availability_dependents']
    availability_dependents.append(new_dependent_id)
    item['availability_dependents'] = list(set(availability_dependents))
    return upsert_item(collection_name=collection_name,item=item)

def remove_availability_dependent_from_npc(npc_id: str, dependent_id: str) -> dict:
    collection_name = 'npcs'
    item = query_collection(collection_name=collection_name, query={'_id': npc_id})[0]
    availability_dependents = item['availability_dependents']
    
    # Removing the dependent from the list
    if dependent_id in availability_dependents:
        availability_dependents.remove(dependent_id)
    
    item['availability_dependents'] = availability_dependents
    return upsert_item(collection_name=collection_name, item=item)

def upsert_npc(world_name:str, npc_name:str, npc_metadata:Optional[dict]=None):
    npc = get_npc(world_name=world_name, npc_name=npc_name)
    item_to_upsert = {} if npc is None else npc
    collection_name = 'npcs'
    _id = '-'.join([collection_name,world_name,npc_name])
    if npc_metadata is not None:
        for k,v in npc_metadata.items():
            item_to_upsert[k] = v
            
    item_to_upsert['world_name']=world_name
    item_to_upsert['npc_name']=npc_name
    item_to_upsert['_id']=_id
    availability_dependencies = []
    if 'id_based_availability_logic' in list(npc_metadata):
        availability_dependencies = re.findall(r'\[(.*?)\]', npc_metadata['id_based_availability_logic'])
        item_to_upsert['availability_dependencies'] = availability_dependencies

    #add this id as an availability dependent to all the dependencies
    add_availability_dependency_links(dependency_ids=availability_dependencies, id=_id)

    #get old item we're potentially replacing
    current_items = query_collection(collection_name=collection_name,query={'_id': _id})
    if len(current_items) == 1:
        item_to_upsert['availability_dependents'] = [] if 'availability_dependents' not in list(current_items[0]) else current_items[0]['availability_dependents']

    upsert_item(collection_name=collection_name,item=item_to_upsert)

def get_npcs_in_world(world_name):
    '''given a world_name get all of the NPCs in that world.'''
    return query_collection(collection_name='npcs',query={'world_name':world_name})

def get_npc(world_name:str, npc_name:str)->dict:
    items = query_collection(collection_name='npcs',query={'world_name': world_name, 'npc_name': npc_name})
    return items[0] if len(items) > 0 else None

def delete_npc(world_name:str,npc_name:str):
    npc = query_collection(collection_name='npcs',query={'world_name':world_name,'npc_name':npc_name})[0]
    if 'availability_dependencies' in npc and len(npc['availability_dependencies']) > 0:
        remove_availability_dependency_links(dependency_ids=npc['availability_dependencies'],id=npc['_id'])
    delete_items(collection_name='npcs',query={'world_name':world_name,'npc_name':npc_name})

def get_available_npcs(world_name:str, user_name:str):
    return get_npcs_in_world(world_name)


#####USER_NPC_INTERACTIONS#####
def get_user_npc_interactions(world_name:str, user_name: str, npc_name:str)->list:
    interactions = query_collection(collection_name='user_npc_interactions',query={'world_name':world_name,'user_name':user_name,'npc_name':npc_name})
    ordered_interactions = sorted(interactions, key=lambda x: datetime.strptime(x['created_at'], "%Y-%m-%d %H:%M:%S"))
    return ordered_interactions


def get_number_of_user_npc_interactions(world_name: str, user_name: str, npc_name: str, scene_id: Optional[str]=None):
    query = {'world_name':world_name,'user_name':user_name,'npc_name':npc_name}
    if scene_id is not None:
        query['scene_id'] = scene_id
    return len(query_collection(collection_name='user_npc_interactions',query=query))

def upsert_user_npc_interaction(
        world_name:str,
        user_name: str,
        npc_name: str,
        scene_id: str,
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
        'scene_id': scene_id,
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
    npc_name: str,
    scene_id: Optional[str]=None,
    num_interactions: Optional[int] = None
)->str:
    query = {'world_name':world_name,'user_name':user_name,'npc_name':npc_name}
    if scene_id is not None:
        query['scene_id']=scene_id
    interactions = query_collection(collection_name='user_npc_interactions',query=query)
    if interactions == []:
        return None
    ordered_interactions = sorted(interactions, key=lambda x: datetime.strptime(x['created_at'], "%Y-%m-%d %H:%M:%S"))
    if num_interactions is not None:
        if num_interactions < len(ordered_interactions):
            ordered_interactions = ordered_interactions[-num_interactions:]
    conversation_lines = [f"{user_name}: {msg['user_message']}\n{npc_name}: {msg['npc_response']}\n" for msg in ordered_interactions]
    return ''.join(conversation_lines).rstrip()



################
#####SCENES#####
################
def insert_scene(world_name: str, scene_info: dict, previous_scene: Optional[str]=None):
    #make sure scene is unique first, else return None
    scene = query_collection(collection_name='scenes',query={'world_name':world_name,'scene_name':scene_info['scene_name']})
    print('previous_scene: ', previous_scene)
    if len(scene) > 0:
        return None
    # this is the current previous scene
    if previous_scene is not None and 'scenes-' in previous_scene:
        previous_scene = query_collection(collection_name='scenes',query={'world_name':world_name,previous_scene:previous_scene})[0]
    elif 'previous_scene_name' in list(scene_info):
        previous_scene = query_collection(collection_name='scenes',query={'world_name':world_name,'scene_name':scene_info['previous_scene_name']})[0]
    
    # this is the scene currently hooked up to that previous scene
    current_scene_hooked_up_to_previous_scene = query_collection(collection_name='scenes',query={'world_name':world_name,'previous_scene':previous_scene['_id']})
    print('current_scene_hooked_up: ', current_scene_hooked_up_to_previous_scene)

    #upsert the new scene
    upserted_scene = {k:v for k,v in scene_info.items()}
    scene_id = '-'.join(['scenes',world_name,get_current_date_formatted_no_spaces()])
    upserted_scene['_id'] = scene_id
    upserted_scene['world_name'] = world_name
    upserted_scene['previous_scene'] = None if previous_scene is None else previous_scene['_id']
    if 'max_number_of_dialogue_exchanges' in list(upserted_scene) and upserted_scene['max_number_of_dialogue_exchanges'] is not None:
        try:
            upserted_scene['max_number_of_dialogue_exchanges'] = int(upserted_scene['max_number_of_dialogue_exchanges'])
        except:
            upserted_scene['max_number_of_dialogue_exchanges'] = None
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
        if 'objectives' in list(item_to_upsert):
            for index, obj_set in enumerate(item_to_upsert['objectives']):
                for index2, obj in enumerate(obj_set):
                    item_to_upsert['objectives'][index][index2]['objective'].replace('.  ','. ')
        if 'max_number_of_dialogue_exchanges' in list(item_to_upsert) and item_to_upsert['max_number_of_dialogue_exchanges'] is not None:
            try:
                item_to_upsert['max_number_of_dialogue_exchanges'] = int(item_to_upsert['max_number_of_dialogue_exchanges'])
            except:
                item_to_upsert['max_number_of_dialogue_exchanges'] = None
        upsert_item(collection_name='scenes',item=item_to_upsert)
        return item_to_upsert
        
    
def get_scene(scene_id: str)->dict:
    scenes = query_collection(collection_name='scenes',query={'_id':scene_id})
    if scenes == []:
        return None
    else:
        scene=scenes[0]
        #this is for converting old objectives format of List[List[str]] -> List[List[Dict]]
        old_objectives = scene['objectives']
        if isinstance(old_objectives, list) and len(old_objectives) > 0:
            if isinstance(old_objectives, list) and len(old_objectives[0]) > 0:
                if isinstance(old_objectives[0][0], dict):#scene objectives of correct format lready
                    new_objectives = old_objectives
                else:#scene objectives are of the old format and need switching
                    new_objectives = [[{"objective": item} for item in inner_list] for inner_list in scene['objectives']]
        scene['objectives'] = new_objectives
        return scene


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
        scene_objectives = {objective['objective']: 'not_completed' for sublist in query_collection(collection_name='scenes',query={'_id': scene_id})[0]['objectives'] for objective in sublist}
    else:
        scene_objectives = items[0]['objectives_completed']
    
    from fuzzywuzzy import process
    for obj, comp in objectives_completed.items():
        if comp == "completed":

            # Find best match in scene_objectives
            best_match, score = process.extractOne(obj, scene_objectives.keys())

            # If the best match score is greater than a certain threshold
            # then consider it a match. You can adjust this threshold.
            threshold = 80
            if score > threshold:
                scene_objectives[best_match] = "completed"
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
    completed_objectives = get_scene_objectives_completed(scene_id=scene_id,user_name=user_name)
    if completed_objectives is None:
        objectives_completed = []
        objectives_available = [obj['objective'] for obj in objectives[0]]
        objectives_unavailable = [obj['objective'] for sublist in objectives[1:] for obj in sublist]
    else:
        objectives_completed = []
        objectives_available = []
        objectives_unavailable = []
        for index, objective_set in enumerate(objectives):
            #if all objectives completed, extend the objectives completed list
            if all(completed_objectives.get(objective['objective']) == "completed" for objective in objective_set): 
                objectives_completed.extend([obj['objective'] for obj in objective_set])
            else:
                objectives_completed.extend([obj['objective'] for obj in objective_set if completed_objectives.get(obj['objective']) == "completed"])
                objectives_available = [obj['objective'] for obj in objective_set if completed_objectives.get(obj['objective']) == "not_completed"]
                if index+1 < len(objectives):
                    objectives_unavailable = [obj['objective'] for sublist in objectives[index+1:] for obj in sublist]
                else:
                    objectives_unavailable = []
                break
    output = {'completed': objectives_completed,'available': objectives_available,'unavailable':objectives_unavailable}
    return output

def delete_user_scene_objectives(scene_id: str, user_name:str):
    delete_items(collection_name='scenes',query={'_id':'-'.join(['scene_objectives_completed',scene_id,user_name])}) 

#####################
#####GAME STATUS#####
#####################

def get_progress_of_user_in_game(world_name: str, user_name: str)->str:
    '''Returns the scene_id that a user is up to for some world'''
    items = query_collection(collection_name='progress_of_user_in_game',query={'world_name': world_name,'user_name':user_name})
    if len(items) > 0:
        return items[0]['scene_id']
    else:
        #return the first scene of the world
        starting_scene = get_starting_scene_of_world(world_name=world_name)
        if starting_scene is not None:
            return starting_scene['_id']
        else:
            return None
        
def progress_user_to_next_scene(world_name:str, user_name:str):
    '''Progresses the user to the next scene in the game in the DB'''
    scene_id = get_progress_of_user_in_game(world_name=world_name,user_name=user_name)
    next_scene = get_next_scene(scene_id=scene_id)
    if next_scene is not None:
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


#####################
######KNOWLEDGE######
#####################

def upsert_knowledge(world_name, tag, knowledge_description, level, knowledge):
    collection_name='knowledge'
    #Write the knowledge to file
    filename=os.path.join(KNOWLEDGE_STORE_PATH,world_name,tag + "_" + str(level) + ".txt")
    os.makedirs(os.path.dirname(filename),exist_ok=True)
    with open(filename,'w') as outfile:
        outfile.write(knowledge)
    item_to_upsert = {
        '_id': '-'.join([collection_name,world_name,tag,str(level)]),
        'world_name': world_name,
        'tag': tag,
        'level': int(level),
        'knowledge_description': knowledge_description,
        'knowledge_filepath': filename,
        'knowledge': knowledge
    }
    upsert_item(collection_name=collection_name,item=item_to_upsert)

def get_knowledge(world_name: str, tag: Optional[str]=None):
    query = {'world_name': world_name}
    if tag is not None:
        query['tag'] = tag
    return query_collection(collection_name='knowledge',query=query)

def get_all_knowledge_for_world(world_name: str):
    return query_collection(collection_name='knowledge',query={'world_name': world_name})

def get_all_unique_knowledge_tags_for_world(world_name: str):
    knowledges = query_collection(collection_name='knowledge',query={'world_name': world_name})
    tags = [k['tag'] for k in knowledges]
    return list(set(tags))

def get_knowledge_files_npc_has_access_to(world_name, npc_name):
    npcs = query_collection(collection_name='npcs',query={'world_name':world_name,'npc_name':npc_name})
    filenames = []
    if len(npcs) > 0:
        npc = npcs[0]
        if 'knowledge_tag_levels' in list(npc):
            npc_knowledge_tag_levels = npc['knowledge_tag_levels']
            for tag, level in npc_knowledge_tag_levels.items():
                for l in range(level + 1): 
                    filenames.append(os.path.join(KNOWLEDGE_STORE_PATH, world_name, tag + "_" + str(l) + ".txt"))
    k_zeros = query_collection(collection_name='knowledge',query={'world_name':world_name,'level':0})
    k_zero_filenames = [f['knowledge_filepath'] for f in k_zeros]
    filenames.extend(k_zero_filenames)
    filenames=list(set(filenames))
    return filenames

# ######################
# #####MISSIONS#########
# ######################

def add_availability_dependent_to_mission(mission_id:str, new_dependent_id: str)->dict:
    collection_name='missions'
    item = query_collection(collection_name=collection_name,query={'_id': mission_id})[0]
    availability_dependents = item['availability_dependents']
    availability_dependents.append(new_dependent_id)
    item['availability_dependents'] = list(set(availability_dependents))
    return upsert_item(collection_name=collection_name,item=item)

def remove_availability_dependent_from_mission(mission_id: str, dependent_id: str) -> dict:
    collection_name = 'missions'
    item = query_collection(collection_name=collection_name, query={'_id': mission_id})[0]
    availability_dependents = item['availability_dependents']
    
    # Removing the dependent from the list
    if dependent_id in availability_dependents:
        availability_dependents.remove(dependent_id)
    
    item['availability_dependents'] = availability_dependents
    return upsert_item(collection_name=collection_name, item=item)


def upsert_mission(
        world_name: str,
        mission_name:str,
        mission_briefing: str,
        possible_outcomes: list,
        id_based_availability_logic: Optional[str]="",
        name_based_availability_logic: Optional[str]=""
        ):
    collection_name = 'missions'
    _id = '-'.join(['missions',world_name,mission_name])
    #get old item we're potentially replacing
    current_items = query_collection(collection_name=collection_name,query={'_id': _id})
    availability_dependents = []
    if len(current_items) == 1 and 'availability_dependents' in list(current_items[0]):
        availability_dependents = current_items[0]['availability_dependents']

    availability_dependencies = re.findall(r'\[(.*?)\]', id_based_availability_logic)
    if len(availability_dependencies) > 0:
        add_availability_dependency_links(dependency_ids=availability_dependencies, id=_id)


    return upsert_item(collection_name=collection_name,item={
        '_id': _id,
        'world_name': world_name,
        'mission_name': mission_name,
        'mission_briefing': mission_briefing,
        'possible_outcomes': possible_outcomes,
        'name_based_availability_logic': name_based_availability_logic,
        'id_based_availability_logic': id_based_availability_logic,
        'availability_dependencies': availability_dependencies,
        'availability_dependents': availability_dependents
    })



# def get_mission(world_name: str, mission_name:str)
def get_mission(mission_id: str):
    items = query_collection(collection_name='missions',query={'_id': mission_id})
    if items is not None and len(items) == 1:
        return items[0]
    else:
        return None

def get_all_missions_for_world(world_name: str):
    return query_collection(collection_name='missions',query={'world_name':world_name})
    
def get_available_missions(world_name: str, user_name:str)->list:
    missions = get_all_missions_for_world(world_name)
    pprint.pprint(missions)
    return missions

def get_mission_id_from_mission_name(world_name: str, mission_name: str)->str:
    items = query_collection(collection_name='missions', query={'world_name':world_name, 'mission_name':mission_name})
    return items[0]['_id'] if len(items)==1 else None

def delete_mission(mission_id: str):
    mission = query_collection(collection_name='missions', query={'_id': mission_id})[0]
    if 'availability_dependencies' in mission and len(mission['availability_dependencies']) > 0:
        remove_availability_dependency_links(dependency_ids=mission['availability_dependencies'],id=mission_id)
    delete_items(collection_name='missions', query={'_id': mission_id})

def convert_availability_logic_from_name_to_id(world_name: str, expr: str) -> str:
    # Convert human-readable format for NPC Objectives to _id based format
    print(expr)
    matches = re.findall(r"\[OBJ '(.*?)' '(.*?)'\]", expr)
    for match in matches:
        npc_name, objective_name = match
        obj_id = get_npc_objective_id_from_objective_name(world_name=world_name, npc_name=npc_name, objective_name=objective_name)
        if obj_id:
            expr = expr.replace(f"[OBJ '{npc_name}' '{objective_name}']", f"[{obj_id}]")

    # Convert human-readable format for Missions to _id based format
    matches = re.findall(r"\[MISS '(.*?)'\]", expr)
    for match in matches:
        mission_name = match
        mission_id = get_mission_id_from_mission_name(world_name=world_name, mission_name=mission_name)
        if mission_id:
            expr = expr.replace(f"[MISS '{mission_name}']", f"[{mission_id}]")
    print(expr)
    return expr
    
    

def convert_availability_logic_from_id_to_name(expr: str) -> str:
    # Convert NPC Objectives from ID format to readable format
    matches = re.findall(r"\[(npc_objectives-[\w-]+)\]", expr)
    for npc_objective_id in matches:
        npc_objective = get_npc_objective(npc_objective_id=npc_objective_id)
        if npc_objective:  # Check if the result is not None
            npc_name = npc_objective.get('npc_name', '')
            objective_name = npc_objective.get('objective_name', '')
            if npc_name and objective_name:  # Ensure both names exist
                expr = expr.replace(f"[{npc_objective_id}]", f"[OBJ '{npc_name}' '{objective_name}']")

    # Convert Missions from ID format to readable format
    matches = re.findall(r"\[(missions-[\w-]+)\]", expr)
    for mission_id in matches:
        mission = get_mission(mission_id=mission_id)
        if mission:  # Check if the result is not None
            mission_name = mission.get('mission_name', '')
            if mission_name:  # Ensure mission name exists
                expr = expr.replace(f"[{mission_id}]", f"[MISS '{mission_name}']")
    
    return expr


def evaluate_availability_logic(expr):
    def get_attribute(collection_id, attribute):
        # Split the string at the first '-'
        parts = collection_id.split('-', 1)
        collection_name = parts[0]
        
        if collection_name == 'npc_objectives':
            doc = get_npc_objective(npc_objective_id=collection_id)
        elif collection_name == 'missions':
            doc = get_mission(mission_id=collection_id)
        

        # Return the attribute if it exists, otherwise return None
        return doc.get(attribute, None) if doc else None

    #Return True for the default empty string
    if expr == "":
        return True
    
    # Capture both collection-id and attribute
    matches = re.findall(r'\[(\w+-[\w-]+)\]\.(\w+)', expr)

    for match in matches:
        collection_id, attribute = match
        value = get_attribute(collection_id, attribute)

        # Replace the placeholders with the actual value in the original expression
        expr = expr.replace(f"[{collection_id}].{attribute}", f"'{value}'")

    print(expr)

    # Convert string representation of booleans to Python booleans
    expr = expr.replace("'True'", "True").replace("'False'", "False")
    
    # Evaluate the modified expression
    return eval(expr)




# #################################
# #####USER_MISSION_STATUS#########
# #################################

def upsert_mission_status_for_user():
    pass


def get_available_missions_for_user():
    pass























# ######################
# #####OBSERVATIONS#####
# ######################

# def upsert_observation(observation: str, world_name: str, user_name: str, npc_name: str, time: str):
#     return upsert_item(collection_name='observations',item={
#         '_id': '-'.join(['collections',world_name,user_name,npc_name,get_current_date_formatted_no_spaces()]),
#         'world_name': world_name,
#         'user_name': user_name,
#         'npc_name': npc_name,
#         'observation': observation,
#         'time': time
#     })    

# def get_observations(world_name: str, user_name: str, npc_name: str):
#     return query_collection(collection_name='observations',query={'world_name':world_name,'user_name': user_name,'npc_name':npc_name})


def add_availability_dependency_links(dependency_ids: list, id: str):
    '''add ID as dependent_id to each id in dependency_ids'''
    for dependency_id in dependency_ids:
        collection_name = dependency_id.split('-')[0]
        if collection_name == 'npc_objectives':
            add_availability_dependent_to_npc_objective(npc_objective_id=dependency_id, new_dependent_id=id)
        elif collection_name == 'missions':
            add_availability_dependent_to_mission(mission_id=dependency_id, new_dependent_id=id)
        elif collection_name == 'npcs':
            add_availability_dependent_to_npc(npc_id=dependency_id, new_dependent_id=id)
    
def remove_availability_dependency_links(dependency_ids: list, id: str):
    '''remove ID from dependent_ids for each id in dependency_ids'''
    for dependency_id in dependency_ids:
        collection_name = dependency_id.split('-')[0]
        if collection_name == 'npc_objectives':
            remove_availability_dependent_from_npc_objective(npc_objective_id=dependency_id, dependent_id=id)
        elif collection_name == 'missions':
            remove_availability_dependent_from_mission(mission_id=dependency_id,dependent_id=id)
        elif collection_name == 'npcs':
            remove_availability_dependent_from_npc(npc_id=dependency_id,dependent_id=id)

################################
######Game State Management#####
################################


def init_game_state(user_name: str, world_name: str):
    #Start by getting all of the missions, npcs, and npc objectives
    all_missions_in_world = get_all_missions_for_world(world_name=world_name)
    all_npcs_in_world = get_npcs_in_world(world_name=world_name)
    all_npc_objectives = get_all_npc_objectives_in_world(world_name=world_name)
    for mission in all_missions_in_world:
        if mission['id_based_availability_logic'] == "":
            #then the mission is available
            update_mission_game_state(
                world_name=world_name,
                user_name=user_name,
                mission_id = mission['_id'],
                mission_status="available"
            )
    for npc in all_npcs_in_world:
        if npc['id_based_availability_logic'] == "":
            #then the npc is available to talk with
            update_npc_game_state(
                world_name=world_name,
                user_name=user_name,
                npc_id=npc['_id'],
                npc_status="available"
            )
    for npc_objective in all_npc_objectives:
        if npc_objective['id_based_availability_logic'] == "":
            #then the npc objective is available
            update_npc_objective_game_state(
                world_name=world_name,
                user_name=user_name,
                npc_objective_id=npc_objective['_id'],
                npc_objective_status="available"
            )

def update_mission_game_state(
    world_name: str,
    user_name:str,
    mission_id:str,
    mission_status: Optional[str]=None,
    mission_outcome: Optional[str]=None,
    mission_debrief: Optional[str]=None,
    npcs_sent_on_mission: Optional[list]=None
    )->dict:
    collection_name = 'mission_game_states'
    mission = query_collection(
        collection_name=collection_name,
        query={
        'world_name': world_name,
        'user_name': user_name,
        'mission_id': mission_id,
        }
    )
    if len(mission)==1:
        item_to_upsert = mission[0]
    else:
        item_to_upsert = {
            'world_name': world_name,
            'user_name': user_name,
            'mission_id': mission_id
        }
    if mission_status is not None:
        item_to_upsert['mission_status'] = mission_status
    if mission_outcome is not None:
        item_to_upsert['mission_outcome'] = mission_outcome
    if mission_debrief is not None:
        item_to_upsert['mission_debrief'] = mission_debrief
    if npcs_sent_on_mission is not None:
        item_to_upsert['npcs_sent_on_mission'] = npcs_sent_on_mission
    return upsert_item(collection_name=collection_name,item=item_to_upsert)

def upsert_npc_game_state(
    world_name: str,
    user_name:str,
    npc_id:str,
    npc_status: Optional[str]=None,
    npc_companion_status: Optional[str]=None,
)->dict:
    collection_name='npc_game_states'
    npcs = query_collection(collection_name=collection_name,query={'world_name': world_name,'user_name': user_name,'npc_id': npc_id})
    item_to_upsert = npcs[0] if len(npcs) == 1 else {'world_name': world_name,'user_name': user_name,'npc_id': npc_id}
    if npc_status is not None:
        item_to_upsert['npc_status'] = npc_status
    if npc_companion_status is not None:
        item_to_upsert['npc_companion_status'] = npc_companion_status
    return upsert_item(collection_name=collection_name,item=item_to_upsert)

def upsert_npc_objective_game_state(
    world_name: str,
    user_name:str,
    npc_objective_id:str,
    npc_objective_status: str
)->dict:
    collection_name='npc_objective_game_states'
    return upsert_item(collection_name=collection_name,item=
                {'world_name':world_name,
                 'user_name':user_name,
                 'npc_objective_id':npc_objective_id,
                 'npc_objective_status': npc_objective_status})
    # npc_objectives = query_collection(collection_name=collection_name,query={'world_name':world_name,'user_name':user_name,'npc_objective_id':npc_objective_id})
    # item_to_upsert = npc_objectives[0] if len(npc_objectives) == 1 else {'world_name': world_name,'user_name': user_name,'npc_objective_id': npc_objective_id}
    # if npc_objective_status is not None:
    #     item_to_upsert

def update_npc_game_state(world_name: str, user_name: str, npc_id: str)->dict:
    pass

def update_npc_objective_game_state(world_name: str, user_name: str, npc_objective_id:str)->dict:
    pass


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
    return None if items is None else items[0]

def play_test_scene_in_renpy(world_name: str, scene_id: str):
    user_name='James Thomas Stanhope'
    reset_game_for_user(world_name=world_name, user_name=user_name)
    set_renpy_init_state(world_name=world_name,user_name=user_name)
    set_scene_the_user_is_in(world_name=world_name,user_name=user_name,scene_id=scene_id)
    os.system('pkill renpy')
    os.system(RENPY_SH_PATH + " &")

def play_world_in_renpy(world_name: str, user_name: str):
    #First reset the scene that the player is in; delete the objectives completed and user-npc-interactions
    current_scene_id = get_progress_of_user_in_game(world_name=world_name, user_name=user_name)
    delete_items(collection_name='user_npc_interactions',query={'user_name':user_name, 'scene_id': current_scene_id})
    delete_items(collection_name='scene_objectives_completed', query={'user_name':user_name,'_id': current_scene_id})
    
    set_renpy_init_state(world_name=world_name,user_name=user_name)
    os.system('pkill renpy')
    os.system(RENPY_SH_PATH + " &")
