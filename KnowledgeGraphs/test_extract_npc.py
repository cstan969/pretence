from llama_index import VectorStoreIndex, SimpleDirectoryReader
import pprint
from llama_index import StorageContext, load_index_from_storage
import os


class KgExtraction():

    def __init__(self, world_name):
        self.world_name=world_name

    def extract_from_kg(self,query):
        storage_context = StorageContext.from_defaults(persist_dir=os.path.join(os.getenv('PRETENCE_PATH'),'KnowledgeGraphs',self.world_name,'storage'))
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return response.response.lstrip().rstrip()

    def extract_npc_from_kg(self,npc_name):
        return {
            "npc_name": npc_name,
            "location": self.extract_from_kg("Where is {npc_name}".format(npc_name=npc_name)),
            "personality": self.extract_from_kg('What is the personality of {npc_name}'.format(npc_name=npc_name)),
            "physical_appearance": self.extract_from_kg('What is the physical appearance of {npc_name}?'.format(npc_name=npc_name)),
            "backstory": self.extract_from_kg('What is the backstory of {npc_name}?'.format(npc_name=npc_name)),
            "goals": self.extract_from_kg('What is the Goal of {npc_name}'.format(npc_name=npc_name)),
            "weaknesses": self.extract_from_kg('What are the weaknesses and failings of {npc_name}?'.format(npc_name=npc_name)),
        }

kge = KgExtraction(world_name='TraumaGame')
npc = kge.extract_npc_from_kg('Callum')
print(npc)