from KnowledgeBase.knowledge_retriever import *
import pprint

def test_knowledge_retriever():
    retriever = LlamaIndexKnowledgeAgent(world_name='TraumaGame',
        npc_name='Callum',
        user_name='James Thomas Stanhope')
    output = retriever.method_llamaindex_agent(user_message='Can you tell me more about Sunken Hearth??')
    print(output)

def test_extract_knowledge_for_user_npc_interaction():
    knowledge = extract_knowledge_for_user_npc_interaction(world_name='TraumaGame',
        npc_name='Callum',
        user_name='James Thomas Stanhope',user_message='Can you tell me more about Sunken Hearth??')
    print(knowledge)

# test_knowledge_retriever()
test_extract_knowledge_for_user_npc_interaction()