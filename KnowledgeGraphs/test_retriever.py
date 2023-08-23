from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import GPT4AllEmbeddings
import json


# Load and split dir docs
loader = DirectoryLoader('/home/carl/Pretence/KnowledgeGraphs/Fun with Food/knowledge', glob="**/*.json", loader_cls=TextLoader)
data = loader.load()
print('doc count: ', len(data))
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# for doc in data:
#     print('---')
#     print(doc.page_content)
#     print(json.loads(doc.page_content))
#     print(type(doc.page_content))
for doc in data:
    print('---')
    # print(doc)
    print(type(doc))
    # print(doc.page_content)

splits = text_splitter.split_documents([json.loads(doc.page_content)['data'] for doc in data])
# print(splits)
# print('len(splits): ', len(splits))

# # Extract tags for each split/document
# metadatas = [{"tags": doc["metadata"]["tags"]} for doc in data]
# print(len(metadatas))

# # Create vectorstore with splits and their respective metadata
# vectorstore = Chroma.from_documents(
#     documents=splits,
#     embedding=GPT4AllEmbeddings(),
#     metadatas=metadatas,
#     persist_directory='Fun with Food'
# )

# # Query the vectorstore
# question = "do all food beings fear humanity?"
# docs = vectorstore.similarity_search(question, k=5)
# print('num docs: ', len(docs))
# for doc in docs:
#     print('---')
#     print(doc.page_content)


