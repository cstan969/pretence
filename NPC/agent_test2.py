from llama_index import download_loader, VectorStoreIndex, ServiceContext
from pathlib import Path

UnstructuredReader = download_loader("UnstructuredReader", refresh_cache=True)

# from llama_index import VectorStoreIndex, SimpleDirectoryReader

# # documents = SimpleDirectoryReader('data').load_data()
# # index = VectorStoreIndex.from_documents(documents)
# # index.storage_context.persist()

# from llama_index import StorageContext, load_index_from_storage
# # rebuild storage context
# storage_context = StorageContext.from_defaults(persist_dir="./HP/storage")
# # load index
# index = load_index_from_storage(storage_context)


import os
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from llama_index import ListIndex, LLMPredictor
from langchain import OpenAI
from llama_index.indices.composability import ComposableGraph
from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_chat_agent, IndexToolConfig
# define a decompose transform
from llama_index.indices.query.query_transform.base import DecomposeQueryTransform
from llama_index.query_engine.transform_query_engine import TransformQueryEngine




from llama_index import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader(os.path.join(os.getenv('PRETENCE_PATH'),'KnowledgeGraphs','TraumaGame','data')).load_data()
index = VectorStoreIndex.from_documents(documents)


llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, max_tokens=512))
decompose_transform = DecomposeQueryTransform(
    llm_predictor, verbose=True
)
# define custom query engines
custom_query_engines = {}
for index in index_set.values():
    query_engine = index.as_query_engine()
    query_engine = TransformQueryEngine(
        query_engine,
        query_transform=decompose_transform,
        transform_extra_info={'index_summary': index.index_struct.summary},
    )
    custom_query_engines[index.index_id] = query_engine
custom_query_engines[graph.root_id] = graph.root_index.as_query_engine(
    response_mode='tree_summarize',
    verbose=True,
)