
from mongodb.mongo_fncs import (
    get_mission,
    get_npc
)

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import json, os, pprint
from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class MissionOutcomes():

    def __init__(self, world_name: str, user_name: str, mission_id: str, npc_names: list):
        self.world_name = world_name
        self.user_name = user_name
        self.npc_names = npc_names
        self.mission = get_mission(mission_id=mission_id)
        self.mission_name = self.mission['mission_name']
        self.llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)

        # self.llm = LlamaCpp(
        #     model_path="/home/carl/Pretence/models/llama2-chronos-hermes-13b/chronos-hermes-13b-v2.ggmlv3.q5_0.bin",
        #     n_gpu_layers=50,
        #     n_batch=512,
        #     temperature=0.75,
        #     max_tokens=2000,
        #     top_p=1,
        #     callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        #     verbose=True,
        #     n_ctx=2000,
        # )

    def _load_mission_prompt(self):
        return """I am making a video game where I, the player of the game, am the leader of a mercenary guild. As part of the game, I am given missions and I must assign member(s) of the mercenary guild to go on these missions. Depending on the mission, the mission is liable to succeed or fail depending on the mercenary members that I assign to the mission. I am going to give you information about the mission and then also give you information about the mercenary guild member(s) that were assigned to go on the mission."""
    
    def _load_mission_brief(self):
        return "Here is the mission briefing: " + self.mission['mission_briefing']
    
    def _load_possible_mission_outcomes(self):
        possible_outcomes = self.mission['possible_outcomes']
        possible_outcomes_given_npcs = []
        for outcome in possible_outcomes:
            if outcome['npcs'] == [] or outcome['npcs'] == "" or any(value in outcome['npcs'] for value in self.npc_names):
                possible_outcomes_given_npcs.append(outcome)

        formatted_outcomes = []
        for i, outcome in enumerate(possible_outcomes_given_npcs, start=1):
            formatted_outcomes.append(f"{i}. {outcome['outcome_name']} - {outcome['outcome_summary']}")
        outcome_message = "Here are the possible mission outcomes:\n" + "\n".join(formatted_outcomes)


        
        # new_list_of_dicts = [{key: dct[key] for key in ['outcome_name','outcome_summary']} for dct in possible_outcomes_given_npcs]
        # outcome_string = str(new_list_of_dicts)
        return outcome_message

    
    def _load_npc_summaries(self):
        npc_summaries = {}
        for npc_name in self.npc_names:
            npc = get_npc(world_name=self.world_name, npc_name=npc_name)
            personality = npc['personality']
            npc_summaries[npc_name] = personality
        return f"Here are the mercenary member(s) assigned to the mission:\n{npc_summaries}"
        

    

    
        

    def get_mission_outcome_and_debriefing(self):
        prompt_assembly_fncs_in_order = [
            self._load_mission_prompt(), #generic prompt to LLM so it knows what is going on
            self._load_mission_brief(), #the specific mission brief
            self._load_possible_mission_outcomes(), #the possible mission outcomes per the NPCs selected
            self._load_npc_summaries()
        ]
        prompt = "\n\n'''''\n".join([fnc for fnc in prompt_assembly_fncs_in_order])
        template = """{question}
        \n'''''
        Here is additional information for writing 'mission_narrative':
In paragraph 1 introduce the mission's setting and context. Describe the initial problem or challenge that the mercenary guild was tasked with addressing. Highlight the importance of the mission and the potential consequences if left unresolved. Emphasize the mission's specific objectives and potential outcomes, including both success and failure scenarios. This paragraph should lay the foundation for the readers to understand the mission's significance and what's at stake.
In paragraph 2 detail the actions and decisions made by the mercenary or mercenaries assigned to the mission. Describe their approach and strategy and why they chose the method they did. Describe initial interactions with the situation or enemies. Provide a vivid portrayal of the conflict, whether it's a battle, negotiation, or investigation, depending on the nature of the mission. Highlight any challenges or obstacles the mercenaries faced, as well as any moments of tension, suspense, or unexpected twists that occurred during the mission. This paragraph should create a sense of anticipation and engagement as the readers follow the unfolding events.
In paragraph 3 wrap up the account by describing the mission's resolution and its aftermath. Clarify the outcome of the mission, whether it was a success or failure, and how it aligned with the potential outcomes outlined earlier. Explain the consequences of the mercenary or mercenaries' actions on the mission's overall objective and the people or entities involved. Delve into the impact of the resolution on the mercenary characters themselves, both emotionally and in terms of personal growth. Touch on how the mission's completion might influence future quests or interactions within the game world. This paragraph should provide a satisfying conclusion to the mission account while also paving the way for new developments.
The narrative should be written in such a way that the player reads the story as if reading a novel.  mission_narrative should simply be a string.  It should not mention 
        
        '''''
        You must format your output as a JSON value that adheres to the following JSON schema instance:
        'outcome' : the name of the outcome that the NPC chose.
        'mission_narrative_summary': a summary of what happened during the mission.
        'mission_narrative': This should just be a simple python string.  A 3 paragraph long narrative that explains what happened in the mission.  This should be written like a detailed story.
        'npc_observations': a dictionary with keys equal to each mercenary name and values that are a list of memories/observations that the mercenary takes away from the mission.
        'npc_outcome_reasoning': for each potential outcome, explain why the mercenary of mercenaries assigned to this mission might result in said outcome(s)."""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        print(response)
        response = json.loads(response)
        pprint.pprint(response)
        return response

