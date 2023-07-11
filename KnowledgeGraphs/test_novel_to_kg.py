from llama_index import VectorStoreIndex, SimpleDirectoryReader

# documents = SimpleDirectoryReader('data').load_data()
# index = VectorStoreIndex.from_documents(documents)
# index.storage_context.persist()

from llama_index import StorageContext, load_index_from_storage
# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="./HP/storage")
# load index
index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()

# response = query_engine.query("what are the weakness and failings of Harry Potter?")
# print(response)
# response = query_engine.query("Does Harry Potter have any secrets that he currently doesn’t feel comfortable telling anyone?")
# print(response)
query = "what hero archetype is harry potter?"
query = "what are harry potters 3 biggest desires that he cannot accomplish on his own?"
query = "Can you provide me all information pertaining to Hermione?"
response = query_engine.query(query)
print(response)
# response = query_engine.query("What is the personality of Harry Potter?")
# print(response)
# response = query_engine.query("What is the physical appearance of Harry Potter?")
# print(response)
# response = query_engine.query("What is the backstory of Harry Potter?")
# print(response)
# response = query_engine.query("What is the goal of Harry Potter?")
# print(response)