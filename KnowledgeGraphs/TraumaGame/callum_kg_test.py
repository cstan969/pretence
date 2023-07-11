from llama_index import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader('data').load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist()

# from llama_index import StorageContext, load_index_from_storage
# # rebuild storage context
# storage_context = StorageContext.from_defaults(persist_dir="./HP/storage")
# # load index
# index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()
query = "Can you provide me a summary of Callum?"
response = query_engine.query(query)
print(response)