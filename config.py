from langchain.llms.llamacpp import LlamaCpp

RENPY_SH_PATH = '/home/carl/Pretence/renpy-8.1.1-sdk/renpy.sh'

port_allocations={
# 'Vicuna':8000,
'NpcUserInteractionAPI':8001,
'MongoDB':8002,
# 'GameDesignerAIAPI':8003,
# 'ExtractorAPI': 8004,
'TTSAPI':8005
}

TURBO = 'gpt-3.5-turbo'
VICUNA = 'vicuna-7b-1.1-16bit'
STARCODER = 'starcoder'


EXTRACTOR_MODEL= TURBO
GameDesigner_model = TURBO
NpcUserInteraction_model = TURBO
NPCBUILDER_MODEL = LlamaCpp

server = "localhost"
IS_SERVER_OR_CLIENT = server