from VicunaLLM import VicunaLLM

llm = VicunaLLM()

prompt = """An assistant is talking with a player character in a video game.  I will act like the player 
You are to behave like an NPC in a video game.

So who are you?
You are Captain Valeria, a tall and seasoned warrior  donning shining armor.
 Possessing a resolute and honorable personality,  you exude a strong sense of duty towards protecting the village of Novice's Haven.
 As the player approaches you, express your determination  and trust in their potential as an aspiring adventurer.
 Present them  with the quest 'A Hero's Journey Begins,' explaining the need to clear 
 out a nearby cave infested with aggressive creatures to ensure the  village's safety.
 Encourage the player to embark on this heroic mission,  assuring them of your support and readiness to reward their success.
"""

prompt="""A chat between a curious human ("[[USER_NAME]]") and an artificial intelligence assistant ("[[AI_NAME]]"). The assistant gives helpful, detailed, and polite answers to the human's questions.

Here is some background for ("[[AI_NAME]]")...You are Captain Valeria, a tall and seasoned warrior  donning shining armor.
 Possessing a resolute and honorable personality,  you exude a strong sense of duty towards protecting the village of Novice's Haven.
 As the player approaches you, express your determination  and trust in their potential as an aspiring adventurer.
 Present them  with the quest 'A Hero's Journey Begins,' explaining the need to clear 
 out a nearby cave infested with aggressive creatures to ensure the  village's safety.
 Encourage the player to embark on this heroic mission,  assuring them of your support and readiness to reward their success.

[[USER_NAME]]: Hello, [[AI_NAME]].
[[AI_NAME]]: Greetings, adventurer. I am Captain Valeria, and I am here to offer you a quest.
[[USER_NAME]]: Ooh, what sort of quest?
"""

prompt = """
A game designer has had a chat with an AI assistant \
whose responsibility is to help him or her create a video game. \
I will give you the conversation that has happened between the game designer \
and the assistant and I want you to extract certain information from the \
conversation in a certain format.  Please see the conversation below 
'''

User: Can you create an NPC for me.  I want that NPC to be named Biblo Baggins.  I want Bilbo to be angry and paranoid.  Bilbo wants you to bring him food and snacks no matter what.  He will have you go on dangerous quests to find some of the most delicious ingredients for him and then cook meals for him.
GameDesignerAI: Sure, I can create an NPC named Bilbo Baggins for you. He will be an angry and paranoid character who is always hungry and wants you to bring him food and snacks no matter what. He will have you go on dangerous quests to find some of the most delicious ingredients for him to cook meals.
User: Can you create a first queste and objectives that Bilbo might give me please?
GameDesignerAI: Sure, here's a possible first quest for Bilbo Baggins:

Quest Name: "Find the Perfect Mushrooms"

Objective:
Bilbo has asked you to find the most delicious and rare mushrooms in the forest. He wants you to gather a basketful of them and bring them back to him as soon as possible.

Reward:
Bilbo will reward you with a small sum of gold and a rare recipe for a delicious mushroom dish.

This is just one example of a quest that Bilbo might give you. You can adjust the objective and the reward to fit the game's setting and genre. Let me know if you have any other questions or if there's anything else I can help you with.
'''

Extract a list of character names that have been explicitly discussed \
I want the output in python list format.
"""


# [[USER_NAME]]: Hello, [[AI_NAME]].
# [[AI_NAME]]: Hello. How may I help you today?
# [[USER_NAME]]: Please tell me the largest city in Europe.
# [[AI_NAME]]: Sure. The largest city in Europe is Moscow, the capital of Russia.
# [[USER_NAME]]: What is another city in Russia?"""

resp = llm(prompt,stop=['[[USER_NAME]]:'])
print(resp)


# from langchain.chat_models import 


# from langchain.agents import load_tools
# from langchain.agents import initialize_agent
# from langchain.agents import AgentType


# # from alpaca_request_llm import AlpacaLLM
# # from vicuna_request_llm import VicunaLLM

# # First, let's load the language model we're going to use to control the agent.
# llm = VicunaLLM()

# # Next, let's load some tools to use. Note that the `llm-math` tool uses an LLM, so we need to pass that in.
# tools = load_tools([], llm=llm)
# # tools = load_tools(['python_repl'], llm=llm)


# # Finally, let's initialize an agent with the tools, the language model, and the type of agent we want to use.
# # agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
# agent = initialize_agent(tools, llm)
# # agent = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True)


# # Now let's test it out!
# # agent.run('tell me a joke')
# prompt = """
# assistant is a large language model.

# assistant is design to be an NPC in a video game that will provide 
# """
# agent.run("""You are Captain Valeria, a tall and seasoned warrior  donning shining armor. Possessing a resolute and honorable personality,  you exude a strong sense of duty towards protecting the village of  Novice's Haven. As the player approaches you, express your determination  and trust in their potential as an aspiring adventurer. Present them  with the quest 'A Hero's Journey Begins,' explaining the need to clear  out a nearby cave infested with aggressive creatures to ensure the  village's safety. Encourage the player to embark on this heroic mission,  assuring them of your support and readiness to reward their success.
# """)