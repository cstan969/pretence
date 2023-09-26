
from mongodb.mongo_fncs import (
    get_mission,
    get_npc,
    update_mission_game_state
)

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import json, os, pprint
from langchain import PromptTemplate, LLMChain
from LlmFunctions.llm_functions import genKGQuestionsGivenMissionBrief, genLTMQuestionsGivenMissionInfo
from KnowledgeBase.knowledge_retriever import LlamaIndexKnowledgeAgent
from LongTermMemory.long_term_memory import LongTermMemory


class MissionOutcomes():

    def __init__(self, world_name: str, user_name: str, mission_id: str, npc_names: list):
        self.world_name = world_name
        self.user_name = user_name
        self.npc_names = npc_names
        self.mission_id = mission_id
        self.mission = get_mission(mission_id=mission_id)
        self.mission_name = self.mission['mission_name']
        self.llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)
        self.formatted_mission_outcomes = self._get_formatted_list_of_possible_mission_outcomes()

    def fix_json(self, json_to_fix):
        template = """I have some broken JSON below that I need to be able to run json.loads() on.  Can you fix it for me? Thanks.\n\n{question}"""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(json_to_fix)
        return response

    def _load_mission_prompt(self):
        return """I am making a video game where I, the player of the game, am the leader of a mercenary guild. As part of the game, I am given missions and I must assign member(s) of the mercenary guild to go on these missions. Depending on the mission, the mission is liable to succeed or fail depending on the mercenary members that I assign to the mission. I am going to give you information about the mission and then also give you information about the mercenary guild member(s) that were assigned to go on the mission."""
    
    def _load_mission_brief(self):
        return "Here is the mission briefing: " + self.mission['mission_briefing']
    
    def _get_formatted_list_of_possible_mission_outcomes(self):
        possible_outcomes = self.mission['possible_outcomes']
        possible_outcomes_given_npcs = []
        for outcome in possible_outcomes:
            if outcome['npcs'] == [] or outcome['npcs'] == "" or any(value in outcome['npcs'] for value in self.npc_names):
                possible_outcomes_given_npcs.append(outcome)

        formatted_outcomes = []
        for i, outcome in enumerate(possible_outcomes_given_npcs, start=1):
            formatted_outcomes.append(f"{i}. {outcome['outcome_name']} - {outcome['outcome_summary']}")
        return formatted_outcomes

    def _load_possible_mission_outcomes(self):
        return "Here are the possible mission outcomes:\n" + "\n".join(self.formatted_mission_outcomes)

    
    def _load_npc_summaries(self):
        npc_summaries = {}
        for npc_name in self.npc_names:
            npc = get_npc(world_name=self.world_name, npc_name=npc_name)
            personality = npc['personality']
            npc_summaries[npc_name] = personality
        return f"Here are the mercenary member(s) assigned to the mission:\n{npc_summaries}"
    
    def _load_knowledge(self):
        questions_for_kg = genKGQuestionsGivenMissionBrief(mission_brief=self.mission['mission_briefing'])
        combined_knowledge = []
        for npc_name in self.npc_names:
            ka = LlamaIndexKnowledgeAgent(world_name=self.world_name,npc_name=npc_name, user_name=self.user_name)
            knowledge = ka.query_index(queries=questions_for_kg)
            combined_knowledge.extend(knowledge)
        return f"Here is the knowledge that the NPCs are aware of that may be pertinent to the mission:\n{combined_knowledge}"
    
    def _load_long_term_memories(self):
        questions_for_ltm = genLTMQuestionsGivenMissionInfo(mission_brief=self.mission['mission_briefing'], formatted_mission_outcomes=self.formatted_mission_outcomes)
        pprint.pprint(questions_for_ltm)
        combined_ltms = []
        for npc_name in self.npc_names:
            ltm = LongTermMemory(world_name=self.world_name,user_name=self.user_name,npc_name=npc_name)
            for q in questions_for_ltm:
                memories = ltm.fetch_memories(q,k=2)
                combined_ltms.extend(memories)
        return f"Here are the companions' relevant long term memories:\n{combined_ltms}"

        
    def get_mission_outcome_and_debriefing(self):
        prompt_assembly_fncs_in_order = [
            self._load_mission_prompt(), #generic prompt to LLM so it knows what is going on
            self._load_mission_brief(), #the specific mission brief
            self._load_possible_mission_outcomes(), #the possible mission outcomes per the NPCs selected
            self._load_npc_summaries(),
            self._load_knowledge(),
            self._load_long_term_memories()
        ]
        prompt = "\n\n'''''\n".join([fnc for fnc in prompt_assembly_fncs_in_order])
        template = """{question}
        \n'''''
        Here is additional information for writing 'mission_narrative':
        Generate a mission narrative for a game using the following structure: Begin with a 'Brief Recap' that summarizes the mission's objective and lists the chosen NPC(s). Transition into 'Departure', painting a scene of the mission preparations and capturing the emotions and thoughts of the NPCs as they start their journey. Introduce 'Challenges & Encounters', detailing the obstacles or confrontations the NPCs face, adding tension and action. As the narrative unfolds, highlight 'Decision Points', emphasizing critical choices made by NPCs and showing their consequences. Build the story to its 'Climax', narrating the peak and most intense moments of the mission. Follow with the 'Outcome', describing whether the mission was a success or failure and the direct consequences of NPC actions. Detail the 'Aftermath', illustrating post-mission events, the NPCs' return, and any character development. Finally, wrap up with a 'Feedback Loop' that offers reflection on the mission, player choices, and hints for future strategy. Using this structure, craft a dynamic mission narrative based on specific player choices and mission details.    
        
        '''''
        You must format your output as a JSON value that adheres to the following JSON schema instance:
        'outcome' : the name of the outcome that the NPC chose.
        'mission_narrative_summary': a summary of what happened during the mission.
        'mission_narrative': This should just be a simple python string.  A 3 paragraph long narrative that explains what happened in the mission.  This should be written like a detailed story.
        'npc_observations': a dictionary with keys equal to each mercenary name and value should be a list of strings that account for the narrative from the perspective from each NPC.  The output should be a list of observations.
        'npc_outcome_reasoning': for each potential outcome, explain why the mercenary of mercenaries assigned to this mission might result in said outcome(s)."""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        # print(response)
        try:
            response = json.loads(response)
        except:
            response = self.fix_json(response)
            response = json.loads(response)
        # pprint.pprint(response)

        #Add observations to Companions' LTMs
        for npc_name in self.npc_names:
            ltm = LongTermMemory(world_name=self.world_name, user_name=self.user_name,npc_name=npc_name)
            ltm.add_memories_from_mission_debrief(mission_debrief=response['mission_narrative'])


        #Update the mission game state
        update_mission_game_state(
            world_name=self.world_name,
            user_name=self.user_name,
            mission_id=self.mission_id,
            mission_status = "completed",
            mission_outcome=response['outcome'],
            mission_debrief=response['mission_narrative'],
            npcs_sent_on_mission=self.npc_names,
            npc_observations=response['npc_observations']
        )

        return response