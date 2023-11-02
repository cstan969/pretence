from LlmFunctions.llm_functions import genMemoriesFromBackstory
from LongTermMemory.long_term_memory import LongTermMemory
from mongodb.mongo_fncs import (
    get_all_missions_for_world,
    get_npcs_in_world,
    get_all_npc_objectives_in_world,
    update_mission_game_state,
    update_npc_game_state,
    update_npc_objective_game_state,
    delete_all_observations_for_clean_default_game_state
)
    

def genMemoriesFromBackstoryAndStoreGameInitIndex(world_name: str, npc_name: str, backstory: str):
    list_of_memories = genMemoriesFromBackstory(backstory=backstory)
    user_name = 'DefaultGameDesignerUserName'
    ltm = LongTermMemory(world_name=world_name,user_name=user_name,npc_name=npc_name)
    #delete the old index
    ltm._delete_faiss()
    #delete the old observations stored in MongoDB
    delete_all_observations_for_clean_default_game_state(world_name=world_name, npc_name=npc_name)
    ltm.add_memories(list_of_memories)
    ltm.genAgSummaryFromBackstory(backstory=backstory)

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
            # ltm = LongTermMemory(world_name=world_name,user_name=user_name,npc_name=npc['npc_name'])
            # if 'npc_ltms' in list(npc):
            #     if len(npc['npc_ltms']) > 0:
            #         print('initializing ', len(npc['npc_ltms']), ' npc memories: ')
            #         ltm.add_memories(npc['npc_ltms'])
        else:
            print("NPC '", npc['npc_name'], "' is unavailable")
    for npc_objective in all_npc_objectives:
        print(npc_objective)
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