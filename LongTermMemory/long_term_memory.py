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

import math, os
import faiss
from langchain_experimental.generative_agents import GenerativeAgentMemory
from config import LONG_TERM_MEMORY_PATH



class LongTermMemory():
    def __init__(self, world_name: str, user_name: str, npc_name: str):
        self.world_name = world_name
        self.user_name = user_name
        self.npc_name = npc_name
        self.vector_store_index_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.user_name, self.npc_name)
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
            reflection_threshold=8,  # we will give this a relatively low number to show how reflection works
        )


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
    
    def _save_faiss(self):
        self.faiss.save_local(self.vector_store_index_path)
        

    def add_memories(self, observations: List[str]):
        for obs in observations:
            self.gen_memory.add_memory(memory_content=obs)
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





# class LongTermMemory():
#     def __init__(self, world_name: str, user_name: str, npc_name: str):
#         self.world_name = world_name
#         self.user_name = user_name
#         self.npc_name = npc_name
#         os.makedirs(os.path.join(LONG_TERM_MEMORY_PATH, self.world_name), exist_ok=True)
#         self.vector_store_index_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.user_name + '-' + self.npc_name + '.index')
#         self.doc_store_path = os.path.join(LONG_TERM_MEMORY_PATH,self.world_name,self.user_name + '-' + self.npc_name + '.json')

#         self.llm = ChatOpenAI(max_tokens=1500)
#         #vector store
#         self.faiss = self._load_faiss()
#         #memory retriever
#         self.memory_retriever = TimeWeightedVectorStoreRetriever(
#             vectorstore=self.faiss, other_score_keys=["importance"], k=15
#         )
#         #generative memory
#         self.gen_memory = GenerativeAgentMemory(
#             llm=self.llm,
#             memory_retriever=self.memory_retriever,
#             verbose=False,
#             reflection_threshold=8,  # we will give this a relatively low number to show how reflection works
#         )


#     def _relevance_score_fn(self, score: float) -> float:
#         """Return a similarity score on a scale [0, 1]."""
#         # This will differ depending on a few things:
#         # - the distance / similarity metric used by the VectorStore
#         # - the scale of your embeddings (OpenAI's are unit norm. Many others are not!)
#         # This function converts the euclidean norm of normalized embeddings
#         # (0 is most similar, sqrt(2) most dissimilar)
#         # to a similarity function (0 to 1)
#         return 1.0 - score / math.sqrt(2)

#     def _load_faiss(self):
#         #get the vector store
#         embeddings_model = OpenAIEmbeddings()
#         embedding_size = 1536
#         index = faiss.IndexFlatL2(embedding_size)
#         if os.path.exists(self.vector_store_index_path):
#             index=faiss.read_index(self.vector_store_index_path)
#             docstore=self._load_doc_store()
#             return FAISS(
#                 embeddings_model.embed_query,
#                 index,
#                 InMemoryDocstore(docstore),
#                 {},
#                 relevance_score_fn=self._relevance_score_fn,
#             )
#         else:
#             return FAISS(
#                 embeddings_model.embed_query,
#                 index,
#                 InMemoryDocstore({}),
#                 {},
#                 relevance_score_fn=self._relevance_score_fn,
#             )
        
#     def _load_doc_store(self):
#         with open(self.doc_store_path, 'r') as f:
#             return json.load(f)

#     def _save_faiss(self):
#         faiss.write_index(self.gen_memory.memory_retriever.vectorstore.index, self.vector_store_index_path)

#     def _save_doc_store(self):
#         with open(self.doc_store_path, 'w') as f:
#             json.dump(self.faiss.docstore._dict, f)
        

#     def add_memories(self, observations: List[str]):
#         print('---add_memories---')
#         print(self.vector_store_index_path)
#         for obs in observations:
#             self.gen_memory.add_memory(memory_content=obs)
#         # print('the memorystream: ', self.gen_memory.memory_retriever.memory_stream)
#         self._save_faiss()
#         self._save_doc_store()
        

#     def fetch_memories(self, observation: str, k: Optional[int] = 5):
#         fetched_memories = self.gen_memory.fetch_memories(observation=observation)
#         for memory in fetched_memories[0:k]:
#             print('---')
#             print(memory.page_content)

































           # query = ""
        # observation = "The player, a curious wanderer, is seeking knowledge and tales from the time before the cataclysm, expressing a deep interest in Callum's past and the history of Eldoria. They display empathy towards Callum's losses and aim to carry forward his legacy by sharing his stories."


    # def save_observations_to
    # def conversation_to_observation()



    #     callum_observations = [
    #     "In days long past, I was celebrated as a hero, known for my courage and spirited joy.",
    #     "I was born in the vibrant city of Eldoria, the youngest among my five siblings.",
    #     "While my siblings found their paths in crafts and trade, my heart pulled me towards the wilderness and the allure of unexplored lands.",
    #     "Many of my adventures became legendary tales; I can still vividly recall my journey across the Treacherous Peaks and the confrontation with the fearsome ice wyrm.",
    #     "The Whispering Caves, a place others thought to be just myths, proved real to me. I ventured inside and returned with unimaginable treasures.",
    #     "My laughter used to be contagious, my stories an escape for many. In my presence, people found solace and hope.",
    #     "The cataclysm devastated everything. Eldoria, my birthplace, was among the first cities to crumble, and with its downfall, I lost my entire family.",
    #     "Grief transformed me. The lively, spirited Callum morphed into a silent, contemplative wanderer.",
    #     "I sought tranquility in the Silent Forest, which now echoed an eerie calm. The spirits of nature bestowed upon me ancient knowledge that furthered my wisdom.",
    #     "The once majestic citadel known as the Ruins of Verathis was another place I ventured to.",
    #     "During my time at the Ruins of Verathis, raiders captured me, seeing an opportunity to ransom me. The ordeal left me with scars, both on my skin and deep within my soul, reminding me daily of the world's newfound cruelty.",
    #     "Sunken Hearth was supposed to be just another stop in my journey, but the people's struggles resonated with the hero still left inside of me. They became my purpose, and their settlement became my refuge, a place I now call home."
    # ]

