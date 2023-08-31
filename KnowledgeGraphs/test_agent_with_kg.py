from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", streaming=True)
from llama_index.tools.ondemand_loader_tool import OnDemandLoaderTool
from llama_index.readers.wikipedia import WikipediaReader
from typing import List
from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
import os
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from pydantic import BaseModel

world_name = 'TraumaGame'
from llama_index import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader("/home/carl/Pretence/KnowledgeGraphs/TraumaGame/data").load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir=os.path.join(world_name,'storage'))
from llama_index import StorageContext, load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir=os.path.join(world_name,'storage'))


from langchain.agents import AgentType


tools = [
    Tool(
        name="LlamaIndex",
        func=lambda q: str(index.as_query_engine().query(q)),
        description="useful for when you need to know more information about the world.",
        return_direct=True,
    ),
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent_executor = initialize_agent(
    tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, memory=memory, verbose=True
)
agent_executor.run('sunken hearth tavern')







# from langchain.llms import LlamaCpp
# from langchain.callbacks.manager import CallbackManager
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# llm = LlamaCpp(
#             model_path="/home/carl/Pretence/models/llama2-chronos-hermes-13b/chronos-hermes-13b-v2.ggmlv3.q5_0.bin",
#             n_gpu_layers=50,
#             n_batch=512,
#             input={"temperature": 0.75, "max_length": 2000, "top_p": 1},
#             callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
#             verbose=True,
#             n_ctx=2000,
#         )

# agent_executor = initialize_agent(
#     tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, memory=memory, verbose=True
# )

# user_message="hey there, can you tell me about what's happened since I was sleeping?"
# user_message="can you tell me more about the different food factions?"
# agent_executor.run(input=user_message)
# print('here')
