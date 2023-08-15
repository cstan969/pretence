#Store Docs to KG
from llama_index import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader('Fun with Food').load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir = 'Fun with Food/storage')

#Load Docs to Index
from llama_index import StorageContext, load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir="Fun with Food/storage")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()



query = "Can you tell me about the factions of this world?"
response = query_engine.query(query)
print(response)