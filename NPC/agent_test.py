from KnowledgeGraphs.KG import KG
from llama_index.langchain_helpers.agents import IndexToolConfig, LlamaIndexTool, LlamaToolkit
# # from VicunaLLM.VicunaLLM import VicunaLLM
# from langchain.chat_models.vicuna import ChatVicuna
# from langchain.chat_models import ChatOpenAI


kg = KG(world_name='TraumaGame')
query_engine = kg.get_query_engine()

tool_config = IndexToolConfig(
    query_engine=query_engine, 
    name=f"Vector Index zone-sunken_heart",
    description=f"useful for when you want to answer queries about sunken heart",
    tool_kwargs={"return_direct": True}
)
tool = LlamaIndexTool.from_tool_config(tool_config)
index_configs = [tool_config]
toolkit = LlamaToolkit(
    index_configs=index_configs,
)

from llama_index.langchain_helpers.agents import create_llama_chat_agent
from langchain.llms.openai import OpenAIChat
llm = OpenAIChat(temperature=0,model_name='gpt-3.5-turbo')

agent_chain = create_llama_chat_agent(
    toolkit,
    llm,
    verbose=True
)

agent_chain.run(input="Query about sunken heart")




# from llama_index import VectorStoreIndex, SimpleDirectoryReader

# # documents = SimpleDirectoryReader('data').load_data()
# # index = VectorStoreIndex.from_documents(documents)
# # index.storage_context.persist()

# from llama_index import StorageContext, load_index_from_storage
# # rebuild storage context
# storage_context = StorageContext.from_defaults(persist_dir="./HP/storage")
# # load index
# index = load_index_from_storage(storage_context)

# query_engine = index.as_query_engine()




# from langchain.agents import initialize_agent
# from langchain.llms.openai import OpenAIChat
# llm = OpenAIChat(temperature=0,model_name='gpt-3.5-turbo')
# agent = initialize_agent(
#     [lc_tool],
#     llm=llm,
#     agent="structured-chat-zero-shot-react-description",
#     verbose=True
# )
# agent.run("Tell me about Sunken Heart")