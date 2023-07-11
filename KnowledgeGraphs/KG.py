from llama_index import StorageContext, load_index_from_storage
import os


class KG():
    def __init__(self,world_name):
        self.world_name=world_name

    def get_query_engine(self):
        storage_context = StorageContext.from_defaults(persist_dir=os.path.join(os.getenv('PRETENCE_PATH'),'KnowledgeGraphs',self.world_name,'storage'))
        index = load_index_from_storage(storage_context)
        return index.as_query_engine()
