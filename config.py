from langchain.llms.llamacpp import LlamaCpp
import os
RENPY_SH_PATH = os.path.join(os.getenv('PRETENCE_PATH'),'renpy-8.1.1-sdk','renpy.sh')
KNOWLEDGE_STORE_PATH = os.path.join(os.getenv('PRETENCE_PATH'),'KnowledgeBase','knowledge_store')
KNOWLEDGE_INDICIES_PATH = os.path.join(os.getenv('PRETENCE_PATH'),'KnowledgeBase')

from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.chat_models import ChatOpenAI


port_allocations={
# 'Vicuna':8000,
'NpcUserInteractionAPI':8001,
'MongoDB':8002,
# 'GameDesignerAIAPI':8003,
# 'ExtractorAPI': 8004,
'TTSAPI':8005
}

GPT4 = ChatOpenAI(model='gpt-4')
TURBO = ChatOpenAI(model='gpt-3.5-turbo')
VICUNA = 'vicuna-7b-1.1-16bit'
STARCODER = 'starcoder'
LLAMA2_RP = "llama2"






EXTRACTOR_MODEL= TURBO
GameDesigner_model = TURBO
NpcUserInteraction_model = TURBO
NPCBUILDER_MODEL = LlamaCpp

if NpcUserInteraction_model == "llama2":
    NpcUserInteraction_model = LlamaCpp(
            model_path="/home/carl/Pretence/models/llama2-chronos-hermes-13b/chronos-hermes-13b-v2.ggmlv3.q5_0.bin",
            n_gpu_layers=50,
            n_batch=512,
            input={"temperature": 0.75, "max_length": 2000, "top_p": 1},
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=True,
            n_ctx=2000,
        )

server = "localhost"
IS_SERVER_OR_CLIENT = server