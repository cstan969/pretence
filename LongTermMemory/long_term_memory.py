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

from mongodb.mongo_fncs import get_observations


class LongTermMemory():
    def __init__(self, world_name: str, user_name: str, npc_name: str):
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
        #load and set the list of documents, e.g. memory stream
        self.memory_stream_filepath = os.path.join(self.vector_store_index_path, 'memory_stream.pkl')
        if os.path.exists(self.memory_stream_filepath):
            with open(self.memory_stream_filepath, 'rb') as f:
                loaded_memory_stream_obj = dill.load(f)
                self.memory_retriever.memory_stream = loaded_memory_stream_obj
        # self.memory_retriever.memory_stream = [Document(page_content=obs['observation'],metadata={'created_at':datetime.strptime(obs['last_updated'],"%Y-%m-%d %H:%M:%S")}) for obs in get_observations(world_name=world_name,user_name=user_name,npc_name=npc_name)]

        #generative memory
        self.gen_memory = GenerativeAgentMemory(
            llm=self.llm,
            memory_retriever=self.memory_retriever,
            world_name=world_name,
            user_name=user_name,
            npc_name=npc_name,
        )

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
        try:
            if os.path.exists(self.game_designer_vector_store_index_path) and not os.path.exists(self.vector_store_index_path):
                return FAISS.load_local(self.game_designer_vector_store_index_path, OpenAIEmbeddings)
            else:
                return FAISS.load_local(self.vector_store_index_path, OpenAIEmbeddings())
        except:
            embeddings_model = OpenAIEmbeddings()
            embedding_size = 1536
            index = faiss.IndexFlatL2(embedding_size)
            return FAISS(
                embeddings_model.embed_query,
                index,
                InMemoryDocstore({}),
                {},
                relevance_score_fn=self._relevance_score_fn,
            )
        
    def _delete_faiss(self):
        if os.path.exists(self.vector_store_index_path):
            os.remove(self.vector_store_index_path)
    
    def _save_faiss(self):
        self.faiss.save_local(self.vector_store_index_path)
        

    def add_memories(self, observations: List[str]):
        print('into add_memories')
        print(type(observations))
        print(observations)
        for obs in observations:
            self.gen_memory.add_memory(obs)
        # self.gen_memory.add_memories(memory_content=";".join(observations))
        # self.gen_memory.add_memories(memory_content=obs)
        # for obs in observations:
        #     self.gen_memory.add_memory(memory_content=obs)
        
        self._save_faiss()
        self._pickle_memory_stream()
        

    def fetch_memories(self, observation: str, k: Optional[int] = 5):
        fetched_memories = self.faiss.similarity_search_with_relevance_scores(observation, k=k)
        # fetched_memories = self.gen_memory.fetch_memories(observation=observation)[0:k]
        page_contents = [m[0].page_content for m in fetched_memories]
        for memory in fetched_memories:
            print('---')
            print(memory[0].page_content)
            print(memory[1])
        return page_contents
