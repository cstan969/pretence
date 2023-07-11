# from langchain.llms import LlamaCpp
# from langchain import PromptTemplate, LLMChain
# from langchain.callbacks.manager import CallbackManager
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler




# template = """Question: {question}
# Answer: Let's work this out in a step by step way to be sure we have the right answer."""
# prompt = PromptTemplate(template=template, input_variables=["question"])
# callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
# n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
# # Make sure the model path is correct for your system!
# llm = LlamaCpp(
#     model_path="/home/carl/Pretence/llama.cpp/models/vicuna-13b-v1.3.ggmlv3.q4_0.bin",
#     n_gpu_layers=n_gpu_layers,
#     n_batch=n_batch,
#     callback_manager=callback_manager,
#     verbose=True,
# )
# llm_chain = LLMChain(prompt=prompt, llm=llm)
# question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"

# llm_chain.run(question)

from llama_index.indices.query.query_transform.base import DecomposeQueryTransform
from llama_index.query_engine.transform_query_engine import TransformQueryEngine

from llama_index.langchain_helpers.agents import LlamaToolkit, create_llama_chat_agent, IndexToolConfig
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from llama_index import SimpleDirectoryReader, GPTListIndex, PromptHelper, load_index_from_storage, StorageContext
from llama_index import LLMPredictor, ServiceContext, ListIndex, VectorStoreIndex, GPTVectorStoreIndex
from llama_index.indices.composability import ComposableGraph

# define prompt helper
max_input_size = 2048
# set number of output tokens
num_output = 256
# set maximum chunk overlap
max_chunk_overlap = 20
prompt_helper = PromptHelper(max_input_size, num_output, chunk_overlap_ratio=0.1, max_chunk_overlap=max_chunk_overlap)

# # Callbacks support token-wise streaming
# callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# # Verbose is required to pass to the callback manager




# Make sure the model path is correct for your system!
# llm = LlamaCpp(
#     model_path="/home/carl/Pretence/llama.cpp/models/vicuna-13b-v1.3.ggmlv3.q4_0.bin", 
#     verbose=False,
#     max_tokens=256,
#     n_ctx=1024,
#     n_batch=256,
# )
from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(temperature=0,model='gpt-3.5-turbo')
llm_predictor = LLMPredictor(llm=llm)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

# Index the your data
documents = SimpleDirectoryReader('/home/carl/Pretence/KnowledgeGraphs/TraumaGame/data').load_data()
index=VectorStoreIndex.from_documents(documents, service_context=service_context)
index_set = {'data':index}
index_summaries = ['data about the world that Callum knows']
query_engine=index.as_query_engine()


# index = GPTListIndex.from_documents(documents, service_context=service_context)
# index.storage_context.persist(persist_dir="/home/carl/Pretence/KnowledgeGraphs/TraumaGame/index")
# storage_context = StorageContext.from_defaults(persist_dir="./index/")
# index = load_index_from_storage(storage_context, service_context=service_context)

graph = ComposableGraph.from_indices(
    ListIndex, 
    [index], 
    index_summaries=index_summaries,
    service_context=service_context
)

y='data'
index_tool_config = IndexToolConfig(
    query_engine=query_engine, 
    name=f"Vector Index {y}",
    description=f"useful for when you want to answer queries about the world",
    tool_kwargs={"return_direct": True, "return_sources": True},
)
index_configs = [index_tool_config]


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
graph_query_engine = graph.as_query_engine(custom_query_engines=custom_query_engines)
graph_config = IndexToolConfig(
    query_engine=graph_query_engine,
    name=f"Graph Index",
    description="useful for when you need to know something about the world.",
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

# agent_chain.run(input="Hey there, how're you?")
agent_chain.run(input="What can you tell me about callum?")


# # Query and print response
# query_engine = index.as_query_engine()
# response = query_engine.query("What can you tell me about Callum?")
# print(response)