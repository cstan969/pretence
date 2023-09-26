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

from LongTermMemory.long_term_memory import LongTermMemory


#####USERS#####
def upsert_user(user_name:str):
    print('upserting user: ', user_name)
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
    # upsert_npc(world_name=world_name, npc_name='Narrator')
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
    availability_dependents = []
    if 'availability_dependents' in item:
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
    name_based_availability_logic: Optional[str]="",
    effects: Optional[list]=[]
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
        'availability_dependents': availability_dependents,
        'effects': effects
    }
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
    print('getting npc_objective from id: ', npc_objective_id)
    collection_name = 'npc_objectives'
    items = query_collection(collection_name=collection_name,query={'_id':npc_objective_id})
    return items[0] if len(items)==1 else None 

def get_npc_objective_dependents(npc_objective_id: str)->list:
    try:
        return query_collection(collection_name='npc_objectives',query={'_id': npc_objective_id})[0]['availability_dependents']
    except Exception as e:
        return []


#####NPCS#####

def add_availability_dependent_to_npc(npc_id:str, new_dependent_id: str)->dict:
    collection_name='npcs'
    item = query_collection(collection_name=collection_name,query={'_id': npc_id})[0]
    availability_dependents = []
    if 'availability_dependents' in list(item):
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
    if 'id_based_availability_logic' not in list(npc_metadata):
        item_to_upsert['id_based_availability_logic'] = ""
            
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

def get_available_npcs(world_name: str, user_name: str):
    npc_game_states = query_collection(
        collection_name='npc_game_states',
        query={'world_name': world_name, 'user_name': user_name, 'status': "available"}
    )
    return query_collection(collection_name='npcs',query={'_id': {'$in': [npc['npc_id'] for npc in npc_game_states]}})
    
def get_available_npc_objectives_for_user(world_name: str, user_name: str, npc_name: str):
    print('get available objectives for user (into)')
    print(world_name)
    print(user_name)
    query = {'world_name': world_name, 'user_name': user_name, 'status': 'available','npc_name':npc_name}
    print("query = '", query, "'")
    states = query_collection(collection_name='npc_objective_game_states',query=query)
    print('npc objective game states for user: ', states)
    items = query_collection(collection_name='npc_objectives',query={'_id':{'$in': [s['npc_objective_id'] for s in states]}})
    print('npc objectives: ', items)
    return items

def get_npcs_objectives_for_user(world_name: str, user_name: str, npc_name: str)->list:
    return query_collection(collection_name='npc_objective_game_states',query={'world_name': world_name, 'npc_name': npc_name, 'user_name': user_name})

def get_npc_dependents(npc_id: str)->list:
    try:
        return query_collection(collection_name='npcs',query={'_id': npc_id})[0]['availability_dependents']
    except Exception as e:
        return []

def get_npcs_in_world(world_name):
    '''given a world_name get all of the NPCs in that world.'''
    return query_collection(collection_name='npcs',query={'world_name':world_name})

def get_npc_by_id(npc_id)->dict:
    items = query_collection(collection_name='npcs',query={'_id': npc_id})
    return items[0] if len(items) > 0 else None

def get_npc(world_name:str, npc_name:str)->dict:
    items = query_collection(collection_name='npcs',query={'world_name': world_name, 'npc_name': npc_name})
    return items[0] if len(items) > 0 else None

def delete_npc(world_name:str,npc_name:str):
    npc = query_collection(collection_name='npcs',query={'world_name':world_name,'npc_name':npc_name})[0]
    if 'availability_dependencies' in npc and len(npc['availability_dependencies']) > 0:
        remove_availability_dependency_links(dependency_ids=npc['availability_dependencies'],id=npc['_id'])
    delete_items(collection_name='npcs',query={'world_name':world_name,'npc_name':npc_name})


#####USER_NPC_INTERACTIONS#####
def get_user_npc_interactions(world_name:str, user_name: str, npc_name:str)->list:
    interactions = query_collection(collection_name='user_npc_interactions',query={'world_name':world_name,'user_name':user_name,'npc_name':npc_name})
    ordered_interactions = sorted(interactions, key=lambda x: datetime.strptime(x['created_at'], "%Y-%m-%d %H:%M:%S"))
    return ordered_interactions


def get_number_of_user_npc_interactions(world_name: str, user_name: str, npc_name: str):
    query = {'world_name':world_name,'user_name':user_name,'npc_name':npc_name}
    return len(query_collection(collection_name='user_npc_interactions',query=query))

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
    npc_name: str,
    num_interactions: Optional[int] = None
)->str:
    query = {'world_name':world_name,'user_name':user_name,'npc_name':npc_name}
    interactions = query_collection(collection_name='user_npc_interactions',query=query)
    if interactions == []:
        return None
    ordered_interactions = sorted(interactions, key=lambda x: datetime.strptime(x['created_at'], "%Y-%m-%d %H:%M:%S"))
    if num_interactions is not None:
        if num_interactions < len(ordered_interactions):
            ordered_interactions = ordered_interactions[-num_interactions:]
    conversation_lines = [f"{user_name}: {msg['user_message']}\n{npc_name}: {msg['npc_response']}\n" for msg in ordered_interactions]
    return ''.join(conversation_lines).rstrip()


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
                for l in range(int(level) + 1): 
                    filename = os.path.join(KNOWLEDGE_STORE_PATH, world_name, tag + "_" + str(l) + ".txt")
                    filenames.append(filename)
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
    availability_dependents = []
    if 'availability_dependents' in list(item):
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

def get_available_missions(world_name: str, user_name:str):
    available_mission_states = query_collection(
        collection_name='mission_game_states',
        query={'world_name':world_name,'user_name':user_name,'status':"available"}
    )
    return query_collection(collection_name='missions',query={'_id':{'$in':[s['mission_id'] for s in available_mission_states]}})

def get_completed_mission_game_states(world_name: str, user_name:str):
    return query_collection(
        collection_name='mission_game_states',
        query={'world_name':world_name,'user_name':user_name,'status':"completed"})


# def get_mission(: str, mission_name:str)
def get_mission(mission_id: str):
    items = query_collection(collection_name='missions',query={'_id': mission_id})
    if items is not None and len(items) == 1:
        return items[0]
    else:
        return None
    
def get_mission_dependents(mission_id: str)->list:
    try:
        return query_collection(collection_name='missions',query={'_id':mission_id})[0]['availability_dependents']
    except Exception as e:
        return []

def get_all_missions_for_world(world_name: str):
    return query_collection(collection_name='missions',query={'world_name':world_name})
    

def get_mission_id_from_mission_name(world_name: str, mission_name: str)->str:
    items = query_collection(collection_name='missions', query={'world_name':world_name, 'mission_name':mission_name})
    return items[0]['_id'] if len(items)==1 else None

def delete_mission(mission_id: str):
    mission = query_collection(collection_name='missions', query={'_id': mission_id})[0]
    if 'availability_dependencies' in mission and len(mission['availability_dependencies']) > 0:
        remove_availability_dependency_links(dependency_ids=mission['availability_dependencies'],id=mission_id)
    delete_items(collection_name='missions', query={'_id': mission_id})


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


################################
######Game State Management#####
################################

def convert_availability_logic_from_name_to_id(world_name: str, expr: str) -> str:
    # Convert human-readable format for NPC Objectives to _id based format
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


def evaluate_availability_logic(world_name: str, user_name: str, expr:str):
    def get_attribute(collection_id, attribute):
        # Split the string at the first '-'
        parts = collection_id.split('-', 1)
        collection_name = parts[0]
        
        if collection_name == 'npc_objectives':
            doc = get_user_specific_npc_objective_game_state(world_name=world_name, user_name=user_name,npc_objective_id=collection_id)
            # doc = get_npc_objective(npc_objective_id=collection_id)
        elif collection_name == 'missions':
            doc = get_mission(mission_id=collection_id)
            doc = get_user_specific_mission_game_state(world_name=world_name,user_name=user_name,mission_id=collection_id)
        # elif collection_name == 'npcs':
        #     doc = get_npc_by_id(npc_id=collection_id)
        

        # Return the attribute if it exists, otherwise return None
        return doc.get(attribute, None) if doc else None


    #ugly workaround
    print('--evaluate avail logic--')
    print(expr)
    #Return True for the default empty string
    if expr == "":
        return "available"
    
    # Capture both collection-id and attribute
    # matches = re.findall(r'\[(\w+-[\w-]+)\]\.(\w+)', expr)
    matches = re.findall(r'\[([\w\s-]+)\]\.(\w+)', expr)


    for match in matches:
        print('match: ', match)
        collection_id, attribute = match
        print('collection_id: ', collection_id)
        print('attribute: ', attribute)
        value = get_attribute(collection_id, attribute)

        # Replace the placeholders with the actual value in the original expression
        expr = expr.replace(f"[{collection_id}].{attribute}", f"'{value}'")


    # Convert string representation of booleans to Python booleans
    expr = expr.replace("'True'", "True").replace("'False'", "False")
    print(expr)
    
    # Evaluate the modified expression
    return "available" if eval(expr) else "unavailable"

def recheck_availability_for_some_game_state_id(world_name: str, user_name: str, id_to_check:str):
    collection_name = id_to_check.split('-')[0]
    print('recheck availability for ', id_to_check)
    if collection_name == 'npcs':
        npc = get_npc_by_id(npc_id=id_to_check)[0]
        updated_npc_status = evaluate_availability_logic(world_name=world_name,user_name=user_name,expr=npc['id_based_availability_logic'])
        update_npc_game_state(world_name=world_name,user_name=user_name,npc_id=id_to_check,npc_status=updated_npc_status)
    elif collection_name == 'missions':
        mission = get_mission(mission_id = id_to_check)
        print('mission: ', mission)
        current_mission_status = mission['status'] if 'status' in list(mission) else None
        print('current mission status: ', current_mission_status)
        if current_mission_status == 'completed':
            return
        updated_mission_status = evaluate_availability_logic(world_name=world_name,user_name=user_name,expr=mission['id_based_availability_logic'])
        print('updated mission status: ', updated_mission_status)
        update_mission_game_state(world_name=world_name,user_name=user_name,mission_id=id_to_check,mission_status=updated_mission_status)
    elif collection_name == 'npc_objectives':
        npc_objective = get_npc_objective(npc_objective_id=id_to_check)
        current_npc_objective_status = npc_objective['status'] if 'status' in list(npc_objective) else None
        if current_npc_objective_status == 'completed':
            return
        updated_npc_objective_status = evaluate_availability_logic(world_name=world_name,user_name=user_name,expr=npc_objective['id_based_availability_logic'])
        update_npc_objective_game_state(
            world_name=world_name,
            user_name=user_name,
            npc_objective_id=id_to_check,
            npc_objective_status=updated_npc_objective_status,
            npc_name=npc_objective['npc_name']
        )
    print('---end recheck')


def add_availability_dependency_links(dependency_ids: list, id: str):
    '''add ID as dependent_id to each id in dependency_ids'''
    for dependency_id in dependency_ids:
        collection_name = dependency_id.split('-')[0]
        print('collection_name: ', collection_name)
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

def delete_user_world_game_state_items(user_name: str, world_name: str):
    delete_items(collection_name='npc_game_states',query={'user_name': user_name, 'world_name': world_name})
    delete_items(collection_name='npc_objective_game_states',query={'user_name': user_name, 'world_name': world_name})
    delete_items(collection_name='mission_game_states',query={'user_name': user_name, 'world_name': world_name})


def init_game_state(user_name: str, world_name: str):
    #Start by getting all of the missions, npcs, and npc objectives
    all_missions_in_world = get_all_missions_for_world(world_name=world_name)
    all_npcs_in_world = get_npcs_in_world(world_name=world_name)
    all_npc_objectives = get_all_npc_objectives_in_world(world_name=world_name)
    for mission in all_missions_in_world:
        if mission['id_based_availability_logic'] == "":
            print("Mission '", mission['mission_name'], "' is available")
            #then the mission is available
            update_mission_game_state(
                world_name=world_name,
                user_name=user_name,
                mission_id = mission['_id'],
                mission_status="available"
            )
        else:
            print("Mission '", mission['mission_name'], "' is unavailable")
    for npc in all_npcs_in_world:
        if npc['id_based_availability_logic'] == "":
            print("NPC '", npc['npc_name'], "' is available")
            #then the npc is available to talk with
            update_npc_game_state(
                world_name=world_name,
                user_name=user_name,
                npc_id=npc['_id'],
                npc_status="available"
            )
            #init NPC LTM
            ltm = LongTermMemory(world_name=world_name,user_name=user_name,npc_name=npc['npc_name'])
            if 'npc_ltms' in list(npc):
                if len(npc['npc_ltms']) > 0:
                    print('initializing ', len(npc['npc_ltms']), ' npc memories: ')
                    ltm.add_memories(npc['npc_ltms'])
        else:
            print("NPC '", npc['npc_name'], "' is unavailable")
    for npc_objective in all_npc_objectives:
        if npc_objective['id_based_availability_logic'] == "":
            print("Objective '", npc_objective['objective_name'], "' is available")
            #then the npc objective is available
            update_npc_objective_game_state(
                world_name=world_name,
                user_name=user_name,
                npc_objective_id=npc_objective['_id'],
                npc_objective_status="available",
                npc_name=npc_objective['npc_name']
            )
        else:
            print("Objective '", npc_objective['objective_name'], "' is unavailable")

def get_user_specific_mission_game_state(world_name: str, user_name: str, mission_id:str)->dict:
    return query_collection(collection_name='mission_game_states',item={'world_name':world_name,'user_name':user_name,'mission_id':mission_id})[0]

def get_user_specific_npc_objective_game_state(world_name: str, user_name: str, npc_objective_id: str)->dict:
    return query_collection(collection_name='npc_objective_game_states',query={'world_name':world_name,'user_name':user_name,'npc_objective_id':npc_objective_id})[0]

def get_user_specific_npc_game_state(world_name: str, user_name: str, npc_id: str)->dict:
    return query_collection(collection_name='npc_game_states',query={'world_name':world_name,'user_name':user_name,'npc_id':npc_id})[0]

def update_mission_game_state(
    world_name: str,
    user_name:str,
    mission_id:str,
    mission_status: Optional[str]=None,
    mission_outcome: Optional[str]=None,
    mission_debrief: Optional[str]=None,
    npcs_sent_on_mission: Optional[list]=None,
    npc_observations: Optional[dict] = None
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
    previous_mission_status = None
    if len(mission)==1:
        item_to_upsert = mission[0]
        previous_mission_status = mission[0]['status']
    else:
        item_to_upsert = {
            '_id': '-'.join([collection_name,world_name,user_name,mission_id]),
            'world_name': world_name,
            'user_name': user_name,
            'mission_id': mission_id
        }

    if mission_outcome is not None:
        item_to_upsert['mission_outcome'] = mission_outcome
    if mission_debrief is not None:
        item_to_upsert['mission_debrief'] = mission_debrief
    if npcs_sent_on_mission is not None:
        item_to_upsert['npcs_sent_on_mission'] = npcs_sent_on_mission
    if mission_status is not None:
        item_to_upsert['status'] = mission_status
    if npc_observations is not None:
        item_to_upsert['npc_observations'] = npc_observations

    upsert_item(collection_name=collection_name,item=item_to_upsert)

    if mission_status is not None:
        if previous_mission_status != mission_status:
            #get the dependent IDs (game states) that can potentially be effected by this change
            dependents = get_mission_dependents(mission_id=mission_id)
            for dependent in dependents:
                recheck_availability_for_some_game_state_id(
                    world_name=world_name,
                    user_name=user_name,
                    id_to_check = dependent
                )
    
    return item_to_upsert

def get_available_companions(world_name: str, user_name: str)->list:
    companion_statuses = query_collection(collection_name='npc_game_states',query={'world_name':world_name,'user_name':user_name,'npc_companion_status':True})
    print(companion_statuses)
    return [c['npc_name'] for c in query_collection(collection_name='npcs', query={'_id': {'$in': [status['npc_id'] for status in companion_statuses]}})]

def get_completed_missions(world_name: str, user_name: str):

    def merge_dicts(list1, list2):
        # Create a lookup dictionary from list2 based on mission_id
        lookup = {item['_id']: item for item in list2}
        
        # Iterate over list1 and update each dict with fields from the matching dict in list2
        for d in list1:
            matched_dict = lookup.get(d['mission_id'], {})
            d['mission_name'] = matched_dict.get('mission_name')
            d['mission_briefing'] = matched_dict.get('mission_briefing')
        return list1

    completed_mission_game_states = query_collection(collection_name='mission_game_states',query={
        'world_name':world_name,
        'user_name':user_name,
        'status': 'completed'
    })
    print('completed_mission_game_states: ', completed_mission_game_states)
    associated_missions = query_collection(collection_name='missions', query={'_id':{'$in':[gs['mission_id'] for gs in completed_mission_game_states]}})
    print('associated_missions: ', associated_missions)
    return merge_dicts(completed_mission_game_states, associated_missions)


def update_npc_game_state(
    world_name: str,
    user_name:str,
    npc_id:str,
    npc_status: Optional[str]=None,
    npc_companion_status: Optional[bool]=False,
)->dict:
    collection_name='npc_game_states'
    npcs = query_collection(collection_name=collection_name,query={'world_name': world_name,'user_name': user_name,'npc_id': npc_id})
    previous_npc_status = None
    if len(npcs) == 1:
        previous_npc_status = npcs[0]['status']
        item_to_upsert = npcs[0]
    else:
        item_to_upsert = {'_id':'-'.join([collection_name,world_name,user_name,npc_id]),'world_name': world_name,'user_name': user_name,'npc_id': npc_id}
    
    if npc_status is not None:
        item_to_upsert['status'] = npc_status
    if npc_companion_status is not None:
        item_to_upsert['npc_companion_status'] = npc_companion_status

    upsert_item(collection_name=collection_name,item=item_to_upsert)

    if npc_status is not None:
        if previous_npc_status != npc_status:
            #get the dependent IDs (game states) that can potentially be effected by this change
            dependents = get_npc_dependents(npc_id=npc_id)
            for dependent in dependents:
                recheck_availability_for_some_game_state_id(
                    world_name=world_name,
                    user_name=user_name,
                    id_to_check = dependent
                )

    return item_to_upsert

# def get_available_companions(world_name: str, user_name: str):
#     items = query_collection(collection_name='npc_game_states',query={'world_name':world_name,'user_name':user_name,'npc_companion_status': True})
#     return [npc['npc_id'] for npc in items]

def update_npc_objective_game_state(
    world_name: str,
    user_name:str,
    npc_name: str,
    npc_objective_id:str,
    npc_objective_status: str
)->dict:
    '''This function is used to update the status of the npc_object.  After updating the objective status
     we then check for dependents and recheck the status of that dependent game state'''
    collection_name='npc_objective_game_states'
    print('npc_objective_id: ', npc_objective_id)
    user_specific_npc_objectives = query_collection(collection_name=collection_name,query={'npc_objective_id':npc_objective_id})
    

    #Update the Game State Object in DB
    item_to_upsert = {
        '_id':'-'.join([collection_name,world_name,user_name,npc_objective_id]),
        'world_name':world_name,
        'user_name':user_name,
        'npc_name': npc_name,
        'npc_objective_id':npc_objective_id,
        'status': npc_objective_status}
    upsert_item(collection_name=collection_name,item=item_to_upsert)


    previous_npc_objective_status = None
    if len(user_specific_npc_objectives) == 1:
        previous_npc_objective_status = user_specific_npc_objectives[0]['status']
    print('previous status: ', previous_npc_objective_status)

    if npc_objective_status is not None:
        if previous_npc_objective_status != npc_objective_status:
            print('looking to trigger effects')
            #Trigger Effects based on objective completion
            if npc_objective_status == "completed":
                effects = get_npc_objective(npc_objective_id=npc_objective_id)['effects']
                print('effects: ', effects)
                if len(effects) > 0:
                    trigger_effects(world_name=world_name, user_name=user_name, effects=effects)
            print('now onto cascading game states')
            #Cascading Game State Updates
            dependents = get_npc_objective_dependents(npc_objective_id)
            print('dependents: ', dependents)
            for dependent in dependents:
                recheck_availability_for_some_game_state_id(
                    world_name=world_name,
                    user_name=user_name,
                    id_to_check = dependent
                )

    return item_to_upsert


def trigger_effects(world_name: str, user_name: str, effects: list):
    '''trigger various effects that occur as a result of objective_completion, mission_completion etc'''
    for effect in effects:
        if effect['type'] == "Gain NPC as Companion":
            npc_name_to_gain = effect["npc"]
            npc=get_npc(world_name=world_name,npc_name=npc_name_to_gain)
            update_npc_game_state(world_name=world_name,user_name=user_name,npc_id=npc['_id'],npc_companion_status=True)


