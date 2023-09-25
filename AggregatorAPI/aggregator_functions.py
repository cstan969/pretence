from LlmFunctions.llm_functions import genMemoriesFromBackstory
from LongTermMemory.long_term_memory import LongTermMemory

def genMemoriesFromBackstoryAndStoreGameInitIndex(world_name: str, npc_name: str, backstory: str):
    list_of_memories = genMemoriesFromBackstory(backstory=backstory)
    user_name = 'DefaultGameDesignerUserName'
    ltm = LongTermMemory(world_name=world_name,user_name=user_name,npc_name=npc_name)
    ltm._delete_faiss()
    ltm.add_memories(list_of_memories)