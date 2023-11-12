from KnowledgeBase.knowledge_retriever import *
import pprint

def test_knowledge_retriever():
    retriever = LlamaIndexKnowledgeAgent(world_name='TraumaGame',
        npc_name='Callum',
        user_name='James Thomas Stanhope')
    output = retriever.method_llamaindex_agent(user_message='Can you tell me more about Sunken Hearth??')
    print(output)

def test_extract_knowledge_for_user_npc_interaction():
    # knowledge = extract_knowledge_for_user_npc_interaction(world_name='TraumaGame',
    #     npc_name='Callum',
    #     user_name='James Thomas Stanhope',user_message='Can you tell me more about Sunken Hearth??')
    # print(knowledge)

    # query = 'Wait, who are you?  Were you sent here to solve the void crisis as well?'
    # query = "What can you tell me about the device that takes you back in time?"
    # query = "couldnt we just use the warp drive to return home?  you solved the void problem didn't you?"
    query = "what can you tell me about the ChronoVortex?"
    # query = "What do you know about void energy?"
    knowledge = extract_knowledge_for_user_npc_interaction(
        world_name='VoidZip',
        npc_name='Vecepia Alcubierre',
        user_name='CarlVoid23',
        user_message=query)
    print(knowledge)

def test_query_engine():
    query = "What do you know about void energy?"
    ka = LlamaIndexKnowledgeAgent(world_name='VoidZip',
        npc_name='Laiza',
        user_name='CarlVoid19')
    queries = [query]
#     queries = [
#     "What is the level of technological and scientific development in Mier?",
#     "Are inhabitants of Mier familiar with extraplanetary concepts, such as void energy?",
#     "What educational resources or institutions exist in Mier for learning advanced science?",
#     "Has Mier had any historical interactions with space travelers or advanced technologies?",
#     "What is the NPC's personal level of education or expertise in scientific matters?",
#     "How are novel or advanced topics typically received by NPCs in Mier?"
# ]
    responses = ka.query_index(queries=queries)
    pprint.pprint(responses)




# test_knowledge_retriever()
test_extract_knowledge_for_user_npc_interaction()
# test_query()
# test_query_engine()