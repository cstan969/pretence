from datetime import datetime, timedelta
from typing import List
from termcolor import colored
from typing import Optional

import json
from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.vectorstores import FAISS
from langchain import LLMChain, PromptTemplate
from langchain.schema import Document

import math, os
import faiss
from langchain_experimental.generative_agents import GenerativeAgentMemory
from config import LONG_TERM_MEMORY_PATH

from datetime import datetime
import dill

from mongodb.mongo_fncs import get_observations, set_default_generative_agent_summary


class LongTermMemory():
    def __init__(self, world_name: str, user_name: str, npc_name: str):
        print('initializing LTM for:')
        print('world_name: ', world_name)
        print('user_name: ', user_name)
        print('npc_name: ', npc_name)
        self.world_name = world_name
        self.user_name = user_name
        self.npc_name = npc_name
        self.game_designer_user_name = 'DefaultGameDesignerUserName'
        self.vector_store_index_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.user_name, self.npc_name)
        self.game_designer_vector_store_index_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.game_designer_user_name, self.npc_name)
        os.makedirs(self.vector_store_index_path, exist_ok=True)

        
        self.llm = ChatOpenAI(max_tokens=1500)
        
        #load the vector story
        self.faiss = self._load_faiss()
        #init the memory retriever
        self.memory_retriever = TimeWeightedVectorStoreRetriever(
            vectorstore=self.faiss, other_score_keys=["importance"], k=15
        )
        
        #wait, isnt this in FAISS index.pkl already?
        #load and set the list of documents, e.g. memory stream
        self.memory_stream_filepath = os.path.join(self.vector_store_index_path, 'memory_stream.pkl')
        self.default_game_designer_memory_stream_filepath = os.path.join(self.game_designer_vector_store_index_path, 'memory_stream.pkl')
        if os.path.exists(self.memory_stream_filepath):
            with open(self.memory_stream_filepath, 'rb') as f:
                loaded_memory_stream_obj = dill.load(f)
                self.memory_retriever.memory_stream = loaded_memory_stream_obj
                print('successfully loaded memory retriever at: ', self.memory_stream_filepath)
        elif os.path.exists(self.default_game_designer_memory_stream_filepath):
            with open(self.default_game_designer_memory_stream_filepath,'rb') as f:
                loaded_memory_stream_obj = dill.load(f)
                self.memory_retriever.memory_stream = loaded_memory_stream_obj
                print('successfully loaded memory retriever at: ', self.default_game_designer_memory_stream_filepath)

        #OR can create memory retriever from observations in mongoDB 'observations' collection
        # self.memory_retriever.memory_stream = [Document(page_content=obs['observation'],metadata={'created_at':datetime.strptime(obs['last_updated'],"%Y-%m-%d %H:%M:%S")}) for obs in get_observations(world_name=world_name,user_name=user_name,npc_name=npc_name)]

        #generative memory
        self.gen_memory = GenerativeAgentMemory(
            llm=self.llm,
            memory_retriever=self.memory_retriever,
            world_name=world_name,
            user_name=user_name,
            npc_name=npc_name,
        )

        #test to make sure the memory stream we loaded is correct.
        print('len of mem stream genAgMem: ', len(self.gen_memory.memory_retriever.memory_stream))
        print(self.gen_memory.memory_retriever.memory_stream)

    def genAgSummaryFromBackstory(self, backstory: str):
        template = """can you generate an npc summary from this backstory?  It should include a summary of who the npc is (behaviors and traits),
         as well as current motivations, location, disposition with regards to the player, skills, and current status.
         
         [npc_name]
         {npc_name}

         [backstory]
         {backstory}
         
         '''''
         You must format your output as a JSON dictionary that adheres to the following JSON schema instance:
         "role": "role of {npc_name} in the game",
         "personality": "the general personality of {npc_name}",
         "motivations": "the current motivations of {npc_name}",
         "values": "values and or beliefs of {npc_name},
         "location": "where {npc_name} currently is",
         "plans": "any current plans that {npc_name} has"
         """
        prompt_from_template = PromptTemplate(template=template, input_variables=['backstory','npc_name'])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(backstory=backstory,npc_name=self.npc_name)
        print(response)
        response = json.loads(response)
        set_default_generative_agent_summary(world_name=self.world_name,npc_name=self.npc_name,summary=response)
        


    def _pickle_memory_stream(self):
        with open(self.memory_stream_filepath, 'wb') as f:
            dill.dump(self.memory_retriever.memory_stream, f)

    def add_memories_from_mission_debrief(self, mission_debrief):
        print('adding memories')
        # self.add_memories(mission_debrief)
        '''This section of code is designed to have NPCs remember and reflect on mission outcomes.'''
        
        template = """Given the following narrative, I want you to extract an account of the story from {npc_name}'s perspective:\n{mission_debrief}
           
        '''''
        You must format your output as a JSON dictionary that adheres to the following JSON schema instance:
        'observations': A list of strings.  Each string is an observation that accounts for the narrative from the perspective of {npc_name} where an observation is an event directly perceived by an agent. Common observations include behaviors performed by the agent themselves or behaviors that agents perceive being performed by other agents or non-agent objects."""
        prompt_from_template = PromptTemplate(template=template, input_variables=["npc_name","mission_debrief"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(npc_name=self.npc_name, mission_debrief=mission_debrief)
        response = json.loads(response)
        self.add_memories(observations=response['observations'])
        # self.gen_memory.pause_to_reflect()

    def get_relevant_memories_given_mission_brief(self, mission_brief)->list:
        pass

    def _relevance_score_fn(self, score: float) -> float:
        """Return a similarity score on a scale [0, 1]."""
        # This will differ depending on a few things:
        # - the distance / similarity metric used by the VectorStore
        # - the scale of your embeddings (OpenAI's are unit norm. Many others are not!)
        # This function converts the euclidean norm of normalized embeddings
        # (0 is most similar, sqrt(2) most dissimilar)
        # to a similarity function (0 to 1)
        return 1.0 - score / math.sqrt(2)

    def _load_faiss(self):
        #load game specific index if it exists
        if os.path.exists(os.path.join(self.vector_store_index_path,'index.faiss')):
            output = FAISS.load_local(self.vector_store_index_path, OpenAIEmbeddings())
            print('LOADED GAME SAVE SPECIFIC INDEX')
            return output
        #else the default if it exists
        elif os.path.exists(os.path.join(self.game_designer_vector_store_index_path, 'index.faiss')):
            output = FAISS.load_local(self.game_designer_vector_store_index_path, OpenAIEmbeddings())
            print('LOADED DEFAULT INDEX')
            return output
        else:
            embeddings_model = OpenAIEmbeddings()
            embedding_size = 1536
            index = faiss.IndexFlatL2(embedding_size)
            output = FAISS(
                embeddings_model.embed_query,
                index,
                InMemoryDocstore({}),
                {},
                relevance_score_fn=self._relevance_score_fn,
            )
            print('LOADED EMPTY NEW INDEX')
            return output
        
    def _delete_folder_and_contents(self, folder_path):
        try:
            # Check if the path exists and is a directory
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # Remove all files and subdirectories inside the folder
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        os.rmdir(item_path)
                # Remove the empty folder itself
                os.rmdir(folder_path)
                print(f"Deleted folder and its contents: {folder_path}")
            else:
                print(f"Folder does not exist: {folder_path}")
        except Exception as e:
            print(f"Error deleting folder: {e}")
        
    def _delete_faiss(self):
        '''deletes the index itself not the dir'''
        if os.path.exists(self.vector_store_index_path):
            self._delete_folder_and_contents(self.vector_store_index_path)
            # os.remove(self.vector_store_index_path)
    
    def _save_faiss(self):
        self.faiss.save_local(self.vector_store_index_path)
        

    def add_memories(self, observations: List[str]):
        print('into add_memories')
        print(type(observations))
        print(observations)

        for obs in observations:
            self.gen_memory.add_memory(obs)
        
        # print('---here are all of the memories we are pickling:\n',self.memory_retriever.memory_stream,'\n----------')
        
        self._save_faiss()
        self._pickle_memory_stream()
        

    def fetch_memories(self, observation: str, k: Optional[int] = 5):
        fetched_memories = self.faiss.similarity_search_with_relevance_scores(query=observation, k=k)
        # fetched_memories = self.gen_memory.fetch_memories(observation=observation)[0:k]
        page_contents = [m[0].page_content for m in fetched_memories]
        for memory in fetched_memories:
            print('---')
            print(memory[0].page_content)
            print(memory[1])
        return page_contents
