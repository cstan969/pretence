from mongodb.mongo_fncs import get_knowledge_files_npc_has_access_to
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from config import LLAMA2_RP
from langchain import PromptTemplate, LLMChain
import json
from config import KNOWLEDGE_INDICIES_PATH
import os
import shutil
import llama_index
from llama_index import set_global_handler, ServiceContext
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.embeddings import LangchainEmbedding
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent
import chromadb

from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import StorageContext
from llama_index.storage.docstore.simple_docstore import SimpleDocumentStore
from llama_index.vector_stores.simple import SimpleVectorStore
from llama_index.storage.index_store.simple_index_store import SimpleIndexStore
from llama_index import load_index_from_storage, load_indices_from_storage, load_graph_from_storage

from config import KNOWLEDGE_STORE_PATH

from llama_index.vector_stores import ChromaVectorStore

from mongodb.mongo_fncs import get_available_companions, get_formatted_conversational_chain

import pprint




# def summarize_user_npc_interaction(world_name: str, npc_name:str, user_name:str, user_query: str):
#     llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
#     chain = load_summarize_chain(llm, chain_type=convo)
#     print(chain)

def write_knowledge_to_user_journal(world_name: str, user_name: str, knowledge: str):
    user_journal_path = os.path.join(KNOWLEDGE_STORE_PATH, world_name, user_name, 'user_journal.txt')
    file = open(user_journal_path,'a')
    file.write('\n\n' + knowledge)

def write_knowledge_to_tag1(world_name: str, user_name: str, tag: str, knowledge: str):
    knowledge_tag_path = os.path.join(KNOWLEDGE_STORE_PATH, world_name, user_name, tag + '_1.txt')
    file = open(knowledge_tag_path,'a')
    file.write('\n\n' + knowledge)


def extract_knowledge_for_user_npc_interaction_v2(world_name: str, npc_name:str, user_name:str, user_message: str):
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
    template = """given this conversation between a player and NPC, i want to determine what knowledge the NPC has access to so that i can provide it as context to the prompt chain.  Given the conversation, give me a list of questions that I can use to query the llamaindex query_engine.
    the question list should only include unique questions.  try to avoid questions that are too similar to each other.  Generate maximum three questions.
    
    '''''
    [conversation]
    {convo}

    '''''
    Required Output: You must format your output as a JSON dictionary that adheres to a given JSON scehema instance with the following keys:
        "questions": "the python list of questions" """
    prompt_from_template = PromptTemplate(template=template, input_variables=["convo"])
    llm_chain = LLMChain(prompt=prompt_from_template,llm=llm, verbose=True)
    convo=get_formatted_conversational_chain(world_name=world_name,user_name=user_name,npc_name=npc_name,num_interactions=3)
    if convo is None:
        convo = user_message
    else:
        convo += '\n' + "Player" + ': ' + user_message + '\n'
    response = llm_chain.run(convo=convo)
    print('---')
    print(response)
    response = json.loads(response)
    queries = response['questions']
    ka = LlamaIndexKnowledgeAgent(world_name,npc_name,user_name)
    return ka.query_index(queries=queries)
    # return ka.method_llamaindex_agent(user_message)

def extract_knowledge_for_user_npc_interaction(world_name: str, npc_name:str, user_name:str, user_message: str):
    ka = LlamaIndexKnowledgeAgent(world_name,npc_name,user_name)
    return ka.method_llamaindex_agent(user_message)
    

def extract_knowledge_for_missions(world_name: str, npc_name:str, user_name:str, mission_brief: str):
    ka = LlamaIndexKnowledgeAgent(world_name,npc_name,user_name)
    return ka.get_knowledge_given_missions_brief(mission_brief=mission_brief)


class LlamaIndexKnowledgeAgent:
    
    def __init__(self, world_name: str, npc_name: str, user_name: str):
        self.world_name = world_name
        self.npc_name = npc_name
        self.user_name = user_name
        self.base_persist_dir = KNOWLEDGE_STORE_PATH
        self.persist_dir = os.path.join(self.base_persist_dir, world_name, user_name, npc_name)


    def load_index(self):
        db2 = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db2.get_or_create_collection("knowledge")
        embed_model = LangchainEmbedding(
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        )
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        service_context = ServiceContext.from_defaults(embed_model=embed_model)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            service_context=service_context,
        )
        return index

    def create_or_update_kg_llama_index(self):
        os.makedirs(self.persist_dir, exist_ok=True)
        knowledge_files = get_knowledge_files_npc_has_access_to(world_name=self.world_name, npc_name=self.npc_name)

        #User Journal - the user journal is essentially game knowledge the player has figured out that companions have access to
        #if the npc of interest is a companion, then add the user journal to their knowledge
        if self.npc_name in get_available_companions(world_name=self.world_name, user_name=self.user_name):
            knowledge_files.append(os.path.join(KNOWLEDGE_STORE_PATH,self.world_name,self.user_name,'user_journal.txt'))
        knowledge_files = list(set([file for file in knowledge_files if os.path.exists(file)]))


        print('knowledge_files: ')
        pprint.pprint(knowledge_files)
        # create client and a new collection
        db = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db.get_or_create_collection("knowledge")
        # define embedding function
        embed_model = LangchainEmbedding(
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        )
        # load documents
        documents = SimpleDirectoryReader(input_files=knowledge_files).load_data()
        # set up ChromaVectorStore and load in data
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        service_context = ServiceContext.from_defaults(embed_model=embed_model)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, service_context=service_context
        )
        return index


    def method_llamaindex_agent(self, user_message: str):
        # try:
        #     print('loading index')
        #     index = self.load_index()
        #     print('successfull loaded index')
        # except:
        #     print('failed to load index')
        #     index = self.create_or_update_kg_llama_index()
        #     print('successfully created new index')
        index = self.create_or_update_kg_llama_index()
        tools = [
            Tool(
                name="LlamaIndex",
                func=lambda q: str(index.as_query_engine().query(q)),
                description="useful when you need to know more information about the world",
                return_direct=True,
            ),
        ]

        from mongodb.mongo_fncs import get_user_npc_interactions
        # set Logging to DEBUG for more detailed outputs
        memory = ConversationBufferMemory(memory_key="chat_history")
        chat_history = get_user_npc_interactions(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name)
        for interaction in chat_history[-6:]:
            memory.chat_memory.add_user_message(interaction['user_message'])
            memory.chat_memory.add_ai_message(interaction['npc_response'])

        llm = ChatOpenAI(temperature=0)
        agent = initialize_agent(
            tools,
            llm,
            agent="conversational-react-description",
            memory=memory,
        )
        try:
            # response = agent.run(input=user_message)
            # response = agent.run(input=f"Role play as {self.npc_name} in a video game.  You are not an AI assistant.  Given the conversation, retrieve return a summary of relevant knowledge as retrieved from the LlamaIndex tool.  Here is the most recent message from the player: " + user_message)
            response = agent.run(input=f"You are {self.npc_name} in a video game.  You are not an AI assistant.  Given the conversation, retrieve relevant knowledge as retrieved from the LlamaIndex tool.  If no relevant knowledge exists, simply respond with 'I have no relevant knowledge on this topic'.  Here is the most recent message from the player: " + user_message)
            return response
        except Exception as e:
            print('failed to get data from KG (or there is none), returning nothing')
            return ""
        
    def query_index(self, queries: list[str]):
        # try:
        #     print('loading index')
        #     index = self.load_index()
        #     print('successfull loaded index')
        # except:
        #     print('failed to load index')
        #     index = self.create_or_update_kg_llama_index()
        #     print('successfully created new index')
        index = self.create_or_update_kg_llama_index()
        engine = index.as_query_engine()
        outputs = []
        for q in queries:
            output = engine.query(q)
            outputs.append(output.response)
        return outputs
        # tools = [
        #     Tool(
        #         name="LlamaIndex",
        #         func=lambda q: str(index.as_query_engine().query(q)),
        #         description="useful when you need to know more information about the world",
        #         return_direct=True,
        #     ),
        # ]
        # llm = ChatOpenAI(temperature=0)
        # agent = initialize_agent(
        #     tools,
        #     llm,
        #     agent="conversational-react-description"
        # )

        # outputs = []
        # for query in queries:
        #     response = agent.run(query)
        #     outputs.append(response)
        # return outputs




# def method_llamaindex_agent(world_name: str, npc_name:str, user_name:str, user_message: str):
     
    
#     knowledge_files = get_knowledge_files_npc_has_access_to(world_name=world_name, npc_name=npc_name)

#     documents = SimpleDirectoryReader(input_files=knowledge_files).load_data()
#     index = VectorStoreIndex.from_documents(documents=documents)

#     tools = [
#         Tool(
#             name="LlamaIndex",
#             func=lambda q: str(index.as_query_engine().query(q)),
#             description="useful when you need to know more information about the world",
#             return_direct=True,
#         ),
#     ]

#     from mongodb.mongo_fncs import get_user_npc_interactions
#     # set Logging to DEBUG for more detailed outputs
#     memory = ConversationBufferMemory(memory_key="chat_history")
#     chat_history = get_user_npc_interactions(world_name=world_name,user_name=user_name,npc_name=npc_name)
#     for interaction in chat_history:
#         memory.chat_memory.add_user_message(interaction['user_message'])
#         memory.chat_memory.add_ai_message(interaction['npc_response'])

#     llm = ChatOpenAI(temperature=0)
#     agent = initialize_agent(
#         tools,
#         llm,
#         agent="conversational-react-description",
#         memory=memory,
#     )
#     response = agent.run(input=user_message)
#     print('-----response from the agent-----:\n', response)
#     return response

# class LlamaIndexKnowledgeAgent():

#     def __init__(self):
#         pass

# def update_llamaindex_index(world_name: str, npc_name:str, user_name:str):
#      #If the indicies don't exist, then we create them.
#     #the knowledge that an npc has access to
#     knowledge_files = get_knowledge_files_npc_has_access_to(world_name=world_name, npc_name=npc_name)
#     documents = SimpleDirectoryReader(input_files=knowledge_files).load_data()
#     index = VectorStoreIndex.from_documents(documents=documents)



# def method_llamaindex_agent(world_name: str, npc_name:str, user_name:str, user_message: str):
     
    

#     #Start by trying to Load Indicies from File
#     #Persist Directories are Game World, User, NPC-specific
#     base_persist_dir = KNOWLEDGE_STORE_PATH
#     world_user_npc_dir = os.path.join(base_persist_dir, world_name, user_name, npc_name)
#     os.makedirs(world_user_npc_dir, exist_ok=True)
#     storage_context = StorageContext.from_defaults(
#         docstore=SimpleDocumentStore.from_persist_dir(persist_dir=world_user_npc_dir),
#         vector_store=SimpleVectorStore.from_persist_dir(persist_dir=world_user_npc_dir),
#         index_store=SimpleIndexStore.from_persist_dir(persist_dir=world_user_npc_dir),
#     )
#     index = load_index_from_storage(storage_context)
#     # graph = load_graph_from_storage(storage_context, root_id="<root_id>") # loads graph with the specified root_id


   



#     tools = [
#         Tool(
#             name="LlamaIndex",
#             func=lambda q: str(index.as_query_engine().query(q)),
#             description="useful when you need to know more information about the world",
#             return_direct=True,
#         ),
#     ]

#     from mongodb.mongo_fncs import get_user_npc_interactions
#     # set Logging to DEBUG for more detailed outputs
#     memory = ConversationBufferMemory(memory_key="chat_history")
#     chat_history = get_user_npc_interactions(world_name=world_name,user_name=user_name,npc_name=npc_name)
#     for interaction in chat_history:
#         memory.chat_memory.add_user_message(interaction['user_message'])
#         memory.chat_memory.add_ai_message(interaction['npc_response'])

#     llm = ChatOpenAI(temperature=0)
#     agent = initialize_agent(
#         tools,
#         llm,
#         agent="conversational-react-description",
#         memory=memory,
#     )
#     response = agent.run(input=user_message)
#     print('-----response from the agent-----:\n', response)
#     return response



 # #Create docstore from knowledge files
        # knowledge_files = get_knowledge_files_npc_has_access_to(world_name=self.world_name, npc_name=self.npc_name)
        # documents = SimpleDirectoryReader(input_files=knowledge_files).load_data()
        # docstore = SimpleDocumentStore()
        # docstore.add_documents(documents)
        # #create index from documents
        # self.index = VectorStoreIndex.from_documents(documents=documents)
        # self.index.storage_context.persist(self.persist_dir)
        # #create vector store??
        ##create graph store??

        # self.storage_context = StorageContext(
        #     docstore=docstore,
        #     index_store=index_store
        # )

        # self.storage_context.persist(persist_dir=self.world_user_npc_dir)


# def method_gpt4all_knowledge_base(world_name: str, npc_name:str, user_name:str, user_message: str):
#     knowledge_files = get_knowledge_files_npc_has_access_to(world_name=world_name, npc_name=npc_name)
#     if knowledge_files is None:
#         return ""
#     if len(knowledge_files) == 0:
#         return ""
#     print('knowledge files: ', knowledge_files)
#     #this is the past convo
#     convo = get_formatted_conversational_chain(world_name=world_name,user_name=user_name,npc_name=npc_name, num_interactions=3)
#     if convo is None:
#         convo = ""
#     convo += '\nPlayer:' + user_message
#     print('conversation:', convo)

#     llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
#     template = """Given the conversation between a player and an NPC {npc_name}, I need to retrieve relevant knowledge from a knowledge base.  What question or questions should provide {npc_name} with the knowledge that is needed to support the conversation between {npc_name} and the player?
#     The question should utilize proper names (no this or that) so as to properly retrieve knowledge.

#     conversation:
#     {convo}
#     """
#     prompt_from_template = PromptTemplate(template=template, input_variables=["convo","npc_name"])
#     llm_chain = LLMChain(prompt=prompt_from_template,llm=llm, verbose=True)
#     summary = llm_chain.run({'convo':convo,'npc_name':npc_name})
#     print('knowledge_base question: ', summary)

#     docs = [TextLoader(file).load() for file in knowledge_files]
#     docs = [item for sublist in docs for item in sublist]
#     print(docs)
#     text_splitter = TokenTextSplitter(chunk_size=30, chunk_overlap=10)

#     # text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0,separators=["\n\n", "\n", "(?<=\. )", ".  ", "  ", " ", ""])
#     splits = text_splitter.split_documents([doc for doc in docs])
#     # world_index_dir = os.path.join(KNOWLEDGE_INDICIES_PATH,world_name)
#     # shutil.rmtree(world_index_dir)
#     # print(world_index_dir)
#     vectorstore = Chroma.from_documents(
#         documents=splits,
#         embedding=GPT4AllEmbeddings()
#     )
#     docs = vectorstore.similarity_search(summary, k=5)
#     return [doc.page_content for doc in docs]