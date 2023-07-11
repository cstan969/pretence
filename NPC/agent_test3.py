from llama_index import download_loader, VectorStoreIndex, ServiceContext
from pathlib import Path



years = [2022, 2021, 2020, 2019]
UnstructuredReader = download_loader("UnstructuredReader", refresh_cache=True)
loader = UnstructuredReader()
doc_set = {}
all_docs = []
for year in years:
    year_docs = loader.load_data(file=Path(f'/home/carl/llama_index_agent_data/data/UBER/UBER_{year}.html'), split_documents=False)
    # insert year metadata into each year
    for d in year_docs:
        d.metadata = {"year": year}
    doc_set[year] = year_docs
    all_docs.extend(year_docs)
    # initialize simple vector indices + global vector index

# NOTE: don't run this cell if the indices are already loaded! 
index_set = {}
service_context = ServiceContext.from_defaults(chunk_size=512)
for year in years:
    cur_index = VectorStoreIndex.from_documents(doc_set[year], service_context=service_context)
    index_set[year] = cur_index
# Load indices from disk
index_set = {}
for year in years:
    index_set[year] = cur_index



from llama_index import ListIndex, LLMPredictor
from langchain import LlamaCpp
from llama_index.indices.composability import ComposableGraph
# set summary text for each doc
index_summaries = [f"UBER 10-k Filing for {year} fiscal year" for year in years]
print('index_summaries: ', index_summaries)




# llm=LlamaCpp(
#     model_path="/home/carl/Pretence/llama.cpp/models/vicuna-13b-v1.3.ggmlv3.q4_0.bin", 
#     verbose=False,
#     max_tokens=256,
#     n_ctx=1024,
#     n_batch=256,
# )
from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(temperature=0,model='gpt-3.5-turbo')




llm_predictor = LLMPredictor(llm=llm)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
# define a list index over the vector indices
# allows us to synthesize information across each index
graph = ComposableGraph.from_indices(
    ListIndex, 
    [index_set[y] for y in years], 
    index_summaries=index_summaries,
    service_context=service_context
)
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import initialize_agent

from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_chat_agent, IndexToolConfig
# define a decompose transform
from llama_index.indices.query.query_transform.base import DecomposeQueryTransform
from llama_index.query_engine.transform_query_engine import TransformQueryEngine
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
# construct query engine
graph_query_engine = graph.as_query_engine(custom_query_engines=custom_query_engines)
# index configs
index_configs = []
for y in range(2019, 2023):
    query_engine = index_set[y].as_query_engine(
        similarity_top_k=3,
    )
    tool_config = IndexToolConfig(
        query_engine=query_engine, 
        name=f"Vector Index {y}",
        description=f"useful for when you want to answer queries about the {y} SEC 10-K for Uber",
        tool_kwargs={"return_direct": True, "return_sources": True},
    )
    index_configs.append(tool_config)
# graph config
graph_config = IndexToolConfig(
    query_engine=graph_query_engine,
    name=f"Graph Index",
    description="useful for when you want to answer queries that require analyzing multiple SEC 10-K documents for Uber.",
    tool_kwargs={"return_direct": True, "return_sources": True},
    return_sources=True
)

toolkit = LlamaToolkit(
    index_configs=index_configs,
    graph_configs=[graph_config]
)
memory = ConversationBufferMemory(memory_key="chat_history")
agent_chain = create_llama_chat_agent(
    toolkit,
    llm,
    memory=memory,
    verbose=True
)
# agent_chain.run(input="hi, i am bob")



agent_chain.run(input="What were some of the biggest risk factors in 2020 for Uber?")



# cross_query_str = (
#     "Compare/contrast the risk factors described in the Uber 10-K across years. Give answer in bullet points."
# )
# response = agent_chain.run(input=cross_query_str)