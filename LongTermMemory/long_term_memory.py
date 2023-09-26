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

import math, os
import faiss
from langchain_experimental.generative_agents import GenerativeAgentMemory
from config import LONG_TERM_MEMORY_PATH



class LongTermMemory():
    def __init__(self, world_name: str, user_name: str, npc_name: str):
        self.world_name = world_name
        self.user_name = user_name
        self.npc_name = npc_name
        self.game_designer_user_name = 'DefaultGameDesignerUserName'
        self.vector_store_index_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.user_name, self.npc_name)
        self.game_designer_vector_store_index_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.game_designer_user_name, self.npc_name)
        os.makedirs(self.vector_store_index_path, exist_ok=True)


        self.faiss = self._load_faiss()
        self.llm = ChatOpenAI(max_tokens=1500)
        #memory retriever
        self.memory_retriever = TimeWeightedVectorStoreRetriever(
            vectorstore=self.faiss, other_score_keys=["importance"], k=15
        )
        #generative memory
        self.gen_memory = GenerativeAgentMemory(
            llm=self.llm,
            memory_retriever=self.memory_retriever,
            verbose=False,
            reflection_threshold=5,  # we will give this a relatively low number to show how reflection works
        )

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
        

    def fetch_memories(self, observation: str, k: Optional[int] = 7):
        fetched_memories = self.faiss.similarity_search_with_relevance_scores(observation, k=5)
        # fetched_memories = self.gen_memory.fetch_memories(observation=observation)[0:k]
        page_contents = [m[0].page_content for m in fetched_memories]
        for memory in fetched_memories:
            print('---')
            print(memory[0].page_content)
            print(memory[1])
        return page_contents
