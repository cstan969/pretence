
from mongodb.mongo_fncs import (
    get_mission,
    get_npc,
    update_mission_game_state,
    get_knowledge
)

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import json, os, pprint
from langchain import PromptTemplate, LLMChain
from LlmFunctions.llm_functions import genKGQuestionsGivenMissionBrief, genLTMQuestionsGivenMissionInfo
from KnowledgeBase.knowledge_retriever import LlamaIndexKnowledgeAgent, write_knowledge_to_tag1
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

    def fix_json(self, json_to_fix: str):
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
        mission_context = "\n\n'''''\n".join([fnc for fnc in prompt_assembly_fncs_in_order])
        template = """{question}
        \n'''''
        Here is additional information for writing 'mission_narrative':
        Generate a mission narrative for a game using the following structure: Begin with a 'Brief Recap' that summarizes the mission's objective and lists the chosen NPC(s). Transition into 'Departure', painting a scene of the mission preparations and capturing the emotions and thoughts of the NPCs as they start their journey. Introduce 'Challenges & Encounters', detailing the obstacles or confrontations the NPCs face, adding tension and action. As the narrative unfolds, highlight 'Decision Points', emphasizing critical choices made by NPCs and showing their consequences. Build the story to its 'Climax', narrating the peak and most intense moments of the mission. Follow with the 'Outcome', describing whether the mission was a success or failure and the direct consequences of NPC actions. Detail the 'Aftermath', illustrating post-mission events, the NPCs' return, and any character development. Finally, wrap up with a 'Feedback Loop' that offers reflection on the mission, player choices, and hints for future strategy. Using this structure, craft a dynamic mission narrative based on specific player choices and mission details.    
        
        '''''
        You must format your output as a JSON value that adheres to the following JSON schema instance:
    "Summarize the mission's objective": "Provide a concise recap of what the mission seeks to achieve.",
    "List the chosen NPC(s) for the mission": "Identify and provide brief information on the non-player characters selected for the task.",
    "Set the immediate context for the story": "Offer a backdrop or situation that sets the stage for the upcoming mission.",
    "Describe mission preparations": "Narrate the steps, arrangements, or strategies decided upon before embarking on the mission.",
    "Convey NPC emotions/thoughts as the mission starts": "Capture the feelings, mindset, or expectations of the NPCs as they begin their task.",
    "Set the initial tone": "Establish the atmosphere, mood, or general sentiment at the onset of the mission.",
    "Detail obstacles or confrontations faced": "Elaborate on challenges, enemies, or dilemmas the NPCs encountered during their journey.",
    "Create tension and action sequences based on the mission's challenges": "Construct thrilling and suspenseful moments deriving from the mission's hurdles.",
    "Emphasize critical choices made by NPCs": "Highlight decisions or crossroads that had significant impact on the mission's direction.",
    "Relate choices to NPC attributes or prior player decisions": "Connect decisions to the character traits of NPCs or actions taken by the player in previous scenarios.",
    "Show the consequence of these decisions on the mission": "Illustrate the outcomes, results, or repercussions of the choices made during the mission.",
    "Narrate the peak of the mission": "Provide a detailed account of the climax or pinnacle moment of the mission.",
    "Describe the most intense or revealing moment": "Delve into the highlight or major twist of the mission, capturing its intensity.",
    "State mission results (success/failure)": "Clearly announce the outcome of the mission, indicating whether objectives were met or not.",
    "Outline direct consequences of NPC actions": "List the immediate effects, results, or changes brought about by the actions of the NPCs during the mission.",
    "Highlight tangible rewards or setbacks": "Spotlight any physical rewards, information gained, alliances formed, or setbacks faced as a result of the mission's outcome.",
    "Narrate the post-mission events": "Detail events or situations that arise after the main mission concludes.",
    "Describe the NPCs' return and any character development": "Narrate the condition, mindset, or any growth of the NPCs as they return from the mission.",
    "Highlight potential long-term consequences or future hints": "Provide clues, foreshadowing, or implications of the mission's impact on future events or missions."
    "outcome" : "the name of the outcome that the NPC chose."
"""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(mission_context)
        # print(response)
        try:
            response = json.loads(response)
        except:
            response = self.fix_json(response)
            response = json.loads(response)
        pprint.pprint(response)
        outcome = response['outcome']



        #PART 2.  GENERATE FULL NARRATIVE FROM DICTIONARY REPRESENTATION
        template = """{mission_context}
        
        '''''
        [mission_outcome]
        {mission_outcome}
        
        '''''
        [output]
        Write a 3 paragraph narrative of the mission based on the [mission_outcome].  Expand upon the narrative I provided earlier, weaving in dialogue, emotions, actions, and the characters' thought processes, while retaining the perspective of a third-person narrator.  The player, e.g. the mercenary manager, should not be included in the narrative."""
        prompt_from_template = PromptTemplate(template=template, input_variables=["mission_context","mission_outcome"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(mission_context=mission_context, mission_outcome=response)
        print(response)

        #PART 3. Rewrite the narrative "take your time" and make it better
        template = """Can you take a look at the following statement, take your time to figure out what could be improved, 
        and then rewrite the following narrative to make it better?  The narrative should be 3 paragraphs long and roughly 15 sentences.\n\n{narrative}"""
        prompt_from_template = PromptTemplate(template=template, input_variables=["narrative"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(narrative=response)
        print(response)

        

        #PART 4. Acquire entity-specific (e.g. the tags associated with the mission) knowledge from the LLM and add it to the KB(s)
        associated_tags = self.mission['associated_knowledge_tags']
        associated_tags.extend(self.npc_names)
        entities = [get_knowledge(world_name=self.world_name, tag=tag)[0] for tag in associated_tags]
        entities = [{'entity':entity['tag'],'description':entity['knowledge_description']} for entity in entities]
        print('---associated tags: ', associated_tags)
        print('---entities: ', entities)
        
        if len(associated_tags) > 0:
            template = """Given a mission narrative and list of entities I want you to extract knowledge from the mission narrative pertaining to each of those entities.
            I need to be able to store this information in a knowledge base where each entity has it's own Document store.  Divide the information into documents based upon these entities.
            It should be written from the perspective of if some npc knows about the entity, then they would know "such and such".
            '''''
            [entities]={entities}
            
            '''''
            [mission_narrative]={mission_narrative}
            
            '''''
            You must format your output as a JSON value that adheres to the following JSON schema instance:
            "knowledge": A dictionary where the keys are each entity name in [entities] and the values are the knowledge extracted from the [mission_narrative] 
            """
            prompt_from_template = PromptTemplate(template=template, input_variables=["entities", "mission_narrative"])
            llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
            knowledge_response = llm_chain.run(entities=entities, mission_narrative=response)
            print(type(knowledge_response))
            try:
                knowledge_response = json.loads(knowledge_response)
            except:
                print(type(knowledge_response))
                knowledge_response = self.fix_json(knowledge_response)
                print(type(knowledge_response))
                knowledge_response = json.loads(knowledge_response)
                print(type(knowledge_response))
            pprint.pprint(knowledge_response)
            print('-----knowledge response-----')
            print(knowledge_response)
            knowledges = knowledge_response['knowledge']
            for entity in entities:
                knowledge = knowledges[entity['entity']]
                write_knowledge_to_tag1(world_name=self.world_name,user_name=self.user_name,tag=entity['entity'],knowledge=knowledge)

        #PART 5. Add observations to Companions' LTMs
        for npc_name in self.npc_names:
            ltm = LongTermMemory(world_name=self.world_name, user_name=self.user_name,npc_name=npc_name)
            ltm.add_memories_from_mission_debrief(mission_debrief=response)
        


        #Update the mission game state
        update_mission_game_state(
            world_name=self.world_name,
            user_name=self.user_name,
            mission_id=self.mission_id,
            mission_status = "completed",
            mission_outcome=outcome,
            mission_debrief=response,
            npcs_sent_on_mission=self.npc_names
        )

        return {'mission_narrative': response}