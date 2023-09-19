EMOTIONS = ["drunk",
            "angry",
            "trusting",
            "motivated",
            "sad",
            "happy",
            "afraid",
            "compassionate"]


import json, os, pprint, math, asyncio
import regex as re
# from VicunaLLM.VicunaLLM import VicunaLLM
from LongTermMemory.long_term_memory import LongTermMemory

from mongodb.mongo_fncs import (
    get_npc,
    get_formatted_conversational_chain,
    upsert_user_npc_interaction,
    get_world,
    get_available_npc_objectives_for_user,
    update_npc_objective_game_state
)
from config import NpcUserInteraction_model
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI


DEBUGGING = False

class NpcUserInteraction():

    def __init__(self, world_name:str, npc_name:str, user_name:str):
        self.world_name=world_name
        self.npc_name=npc_name
        self.user_name = user_name
        self.llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)
        self.ltm = LongTermMemory(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name)
        # self.llm = ChatOpenAI(model='gpt-4')
        # self.llm = ChatOpenAI(model=NpcUserInteraction_model)
        self.npc = get_npc(world_name,npc_name)

    def _get_speech_pattern(self, npc_emotional_state):
        patterns = {
            "Trust": "use reassuring and reliable language, expressing confidence in the consistency and predictability of a situation or person.",
            "Happiness": "use positive and exuberant words, expressing excitement and delight in their responses.",
            "Sadness": "use somber and reflective language, sharing feelings of melancholy and disappointment.",
            "Anger": "employ strong and assertive language, possibly resorting to aggressive or confrontational responses.",
            "Fear": "use hesitant and anxious language, expressing concerns and apprehensions, but do not use 'um' more than a couple of times",
            "Surprise": "use exclamatory phrases (e.g., 'Wow!', 'No way!') and may ask questions or seek clarification about unexpected events.",
            "Disgust": "employ negative and disdainful language, expressing aversion or revulsion towards certain subjects.",
            "Excitement": "use enthusiastic language with exclamation marks, expressing eagerness and anticipation.",
            "Confusion": "ask for explanations or seek clarification, using uncertain language like, 'I'm not sure what's going on...'.",
            "Calmness": "use composed and measured language, offering explanations or advice in a controlled manner.",
            "Curiosity": "use inquisitive language, asking questions and expressing interest in learning more or discovering new things.",
            "Pride": "talk about accomplishments and achievements modestly, offering insights or advice with a sense of self-assuredness.",
            "Shyness": "use hesitations and cautious language, often expressing self-doubt or uncertainty about interactions, but do not use 'um' more than a couple of times."
        }

        # Filter emotions that meet or exceed their threshold
        sorted_values = dict(sorted(npc_emotional_state.items(), key=lambda item: item[1], reverse=True))
        # Extracting the top two key-value pairs
        top_two_emotions = dict(list(sorted_values.items())[:2])
        relevant_emotions = [emotion for emotion, value in top_two_emotions.items() if value >= 5]
        if len(relevant_emotions) == 0:
            return ""
        
        
        if len(relevant_emotions) == 1:
            output = f"{self.npc_name} is currently feeling {relevant_emotions[0]}. {self.npc_name} should {patterns[relevant_emotions[0]]}"
        elif len(relevant_emotions) == 2:
            output = f"{self.npc_name} is currently feeling {relevant_emotions[0]} and {relevant_emotions[1]}. {self.npc_name} should {patterns[relevant_emotions[0]]}  {self.npc_name} might also {patterns[relevant_emotions[1]]}"
        
        if 'speech_patterns' in list(self.npc) and self.npc['speech_patterns'] != "":
            npc_specific_speech_patterns = self.npc['speech_patterns']
            output += f"{self.npc_name} has some NPC-specific speech patterns that include: {npc_specific_speech_patterns}"

        # Return speech patterns for all above-threshold emotions
        return output



    # def calculate_new_emotional_state(self, npc_emotional_response: dict):
    #     '''
    #     Sample input format:
    #     "npc_emotional_response": {
    #         "drunk": 0,
    #         "angry": 0,
    #         "trusting": 2,
    #         "motivated": 5,
    #         "sad": 0,
    #         "happy": 0,
    #         "afraid": 0,
    #         "compassionate": 0
    #     }'''
    #     initial_emotional_state = get_latest_npc_emotional_state(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name)
    #     if initial_emotional_state is None:
    #         initial_emotional_state = {e:0 for e in EMOTIONS}
    #     final_emotional_state = {}
    #     for emotion, value in npc_emotional_response.items():
    #         if value != 0:
    #             final_emotional_state[emotion] = initial_emotional_state[emotion] + npc_emotional_response[emotion] * self.npc['emotional_susceptibility'][emotion] / 10
    #         else:
    #             final_emotional_state[emotion] = max([initial_emotional_state[emotion] - 0.2,0])
    #     return final_emotional_state
        
    def get_conversation(self):
        convo = get_formatted_conversational_chain(world_name=self.world_name,npc_name=self.npc_name,user_name=self.user_name, num_interactions=12)
        if convo is None:
            return "Player" + ": Placeholder dialog\n" + self.npc_name + ": Placeholder dialog"
        else:
            return convo.replace(self.user_name,'Player')
        
    async def run_prompt_to_get_objective_completion(self, input_response: dict)->dict:
        '''given the current conversation with the current npc, figure out which objectives are completed for the NPC'''
        #conversation
        convo = self.get_conversation()
        available_npc_objectives = get_available_npc_objectives_for_user(world_name=self.world_name, user_name=self.user_name, npc_name=self.npc_name)
        list_of_objectives = [obj['objective_completion_string'] for obj in available_npc_objectives]
        print('list of objectives: ', list_of_objectives)
        template = """Contextual Information:
        {question}

        Required Output: You must format your output as a JSON dictionary that adheres to a given JSON scehema instance with the following keys:
            'objectives_completed': A dict with keys that EXACTLY MATCH the objectives as given in the player_scene_objectives list.  The values for each key value pair in this dict should be either 'completed' or 'not_completed' depending on whether that objective has been completed.
            'objectives_completed_reason': A string that describes why or why not the objective(s) were marked as either completed or not completed."""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)


        prompt = """Based off of the conversation below, which of the conversational objectives have been completed?
        player_scene_objectives:
        {objectives}

        This is the conversation between the player and the NPC so far.
        CONVERSATION:
        {conversation}""".format(objectives=list_of_objectives,conversation=convo)
        response = llm_chain.run(prompt)
        print(response)
        print('type of response in objc prompt: ', type(response))
        try:
            response = json.loads(response)
        except:
            response = self.fix_json(response)
            response = json.loads(response)

        #completed objectives
        for obj in list_of_objectives:
            print(obj)
            if obj['objective_completion_string'] in list(response['objectives_completed']):
                if response['objectives_completed'][obj['objective_completion_string']] == 'completed':
                    update_npc_objective_game_state(
                    world_name=self.world_name,
                    user_name=self.user_name,
                    npc_objective_id=obj['_id'],
                    npc_objective_status="completed"
                    )
            
        # completed_npc_objective_ids = [d['_id'] for d in list_of_objectives if response['objectives_completed'].get(d['objective_completion_string'],'not_completed')) == 'completed']
        # mark the objectives that've been completed as such in DB. 
        # for obj_id in completed_npc_objective_ids:
                # update_npc_objective_game_state(
                # world_name=self.world_name,
                # user_name=self.user_name,
                # npc_objective_id=obj_id,
                # npc_objective_status="completed"
                # )
                 

        print('type of response in objc prompt: ', type(response))
        input_response['objectives_completed'] = response['objectives_completed']
        input_response['objectives_completed_reason'] = response['objectives_completed_reason']
        return input_response

    def fix_json(self, json_to_fix):
        template = """I have some broken JSON below that I need to be able to run json.loads() on.  Can you fix it for me? Thanks.\n\n{question}"""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(json_to_fix)
        return response

    async def post_process_npc_response(self, input_response):
        speech_pattern_prompt_string = self._get_speech_pattern(input_response['npc_emotional_state'])

        prompt = f"""Contextual Information: An NPC, {self.npc_name}, in a video game has responded to the player.  I want you to rewrite {self.npc_name}'s response given certain speech pattern requirements.
        {self.npc_name}'s original response was: {input_response['npc_response']}.
        {self.npc_name}'s current emotional state is as follows, where 0 is minimum and 10 is maximum.
        {input_response['npc_emotional_state']}
        {speech_pattern_prompt_string}
        """
        
        # if 'speech_patterns' in self.npc and self.npc['speech_patterns'] != "":
        #     prompt += '\n' + f"""Here is information regarding {self.npc_name}'s general speech pattern: {self.npc['speech_patterns']}"""
        # else:
        #     prompt += '\n' + f"""Here is information regarding {self.npc_name}'s general speech pattern: {self.npc_name} speaks like a normal average person."""

        template = """{question}
        
        Required Output: You must format your output as a JSON value that adheres to a given JSON scehema instance with the following keys:
        npc_response: the original npc_response
        postprocessed_npc_response: the new npc_response having taken in account the speech pattern requirements.  The NPC communicates with a natural fluency, using varied sentence structures and vocabulary akin to a human conversationalist.  The NPC adjusts their tone and content based on their emotional state, showing nuances like humor, sarcasm, hesitation, or enthusiasm when appropriate.  The NPC response should feel immersive (not a chat bot).
        postprocessed_npc_response_reasoning: should explain why the npc response was changed how it was."""
    
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        # llm_chain = LLMChain(prompt=prompt, llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        response = json.loads(response)
        input_response['postprocessed_npc_response'] = response['postprocessed_npc_response']
        input_response['postprocessed_npc_response_reasoning'] = response['postprocessed_npc_response_reasoning']
        return input_response

    def npc_emotion_and_reasoning(self, user_message)->dict:

        prompt = self._get_prompt()
        prompt += '\n' + "Player" + ': ' + user_message + '\n' + self.npc_name + ': '    
        

        from langchain.output_parsers import StructuredOutputParser, ResponseSchema

      

        template = """Contextual Information: {question} 
        \n'''''\n""" + """You must format your output as a JSON value that adheres to a given JSON scehema instance with the following keys:
            'scene_summary': A summary of what is going on in the scene.  This should include not only conversation but also the purpose of the scene.
            'scene_reasoning': should describe what {npc_name} might do given scene_summary.
            'chat_or_objectives': should describe whether {npc_name} should respond more as a chat bot or an NPC quest giver in this instance.
            'user_message': should simply be the player's last message
            'user_reasoning': should explain {npc_name}'s thought process when analyzing what the player is thinking or trying to do.
            'scene_objectives': should be a re-iteration of the current scene objectives
            'scene_objectives_reasoning': should be the {npc_name}'s thought process when analyzing and determining how to react to scene_objectives
            'chatbot_response': should be {npc_name}'s response to the player's last message that has NOTHING to do with scene_objectives.
            'npc_personal_scene_objectives': should be the npc_personal_objectives and npc_personal_scene_objectives that {npc_name} is currently attempting to fulfill.
            'npc_personal_scene_objectives_reasoning': should be the {npc_name}'s thought process when analyzing and determining how to react based off npc_personal_scene_objectives
            'npc_emotional_state': should be a dict with keys [Trust, Happiness, Sadness, Anger, Fear, Surprise, Disgust, Excitement, Confusion, Calmness, Curiosity, Pride, Shyness] and values from 0-10 where 10 indicates a strong emotional response and 0 indicates no response for {npc_name}.
            'npc_emotional_state_reasoning': should explain the npc_emotional_state of {npc_name}
            'response_summary': should be a summarization of {npc_name}'s thought process when analyzing and determining how to react to the user_message. This reasoning should be based on not only the user_message but also npc_personal_scene_objectives_reasoning and scene_objectives_reasoning and npc_personal_objectives_reasoning.  It should summarize what {npc_name}'s response to the player would be.
            'npc_response': should be {npc_name}'s response to the player's last message.  It should take into account each of the components of this output JSON as explained in response_summary.  {npc_name}'s response should be significantly different than {npc_name}'s previous response and maximum 3 sentences long.""".format(npc_name=self.npc_name)
        

        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        # response = re.search(r'\{(.*)\}', response).group(1) if re.search(r'\{(.*)\}', response) else response
        try:
            response = json.loads(response)
        except:
            response = self.fix_json(response)
            response = json.loads(response)
        return response

    async def message_npc_and_get_response(self, user_message):
        '''Assemble the prompt and query the NPC to get a response'''
        self.user_message = user_message
        #First we have to get the prompt for the NPC agent
        prompt = self._get_prompt()
        prompt += '\n' + "Player" + ': ' + user_message + '\n' + self.npc_name + ': '    

        response = self.npc_emotion_and_reasoning(user_message=user_message)

        # response_objectives, response_speech_patterns = await asyncio.gather(
        #     self.run_prompt_to_get_objective_completion(input_response=response),
        #     self.post_process_npc_response(input_response=response)
        # )
        response_objectives = await self.run_prompt_to_get_objective_completion(input_response=response)
        pprint.pprint(response)
        print(response_objectives)
        # response['npc_response'] = response_speech_patterns['postprocessed_npc_response']
        # response['postprocessed_npc_response_reasoning'] = response_speech_patterns['postprocessed_npc_response_reasoning']
        response['objectives_completed'] = response_objectives['objectives_completed']
        response['objectives_completed_reason'] = response_objectives['objectives_completed_reason']

        #Save interaction to DB
        upsert_user_npc_interaction(
            world_name=self.world_name,
            user_name=self.user_name,
            npc_name=self.npc_name,
            user_message=response['user_message'],
            npc_response=response['npc_response'],
            npc_emotional_response=response['npc_emotional_state'],
            )
    
        

        self.ltm.add_memories([self.user_name + " said to " + self.npc_name + " '" + self.user_message + "'.",
                               self.npc_name + " said to " + self.user_name + " '" + response['npc_response'] + "'."])

        pprint.pprint(response)
        return response
    
    def _load_long_term_memory(self):
        memories = self.ltm.fetch_memories(observation=self.user_message)
        if memories is not None and len(memories) > 0:
            return f"""Here are some memories for {self.npc_name}:
            {memories}"""
        else:
            return ""
    
    def _load_fourth_wall(self):
        '''fourth wall prompt system commands'''
        return """4th Wall System Prompts:\nHere are system level prompts that {npc_name} must follow to maintain the fourth wall in this video game:
        {npc_name} isn't aware of the player. When interacting with the player, {npc_name} must remember that they are a part of the world.
        {npc_name} must treat the player as a fellow resident of the world.
        {npc_name} must always act according to the traits and logic of the narrative.
        {npc_name} must not assist the player as a standard chat assistant would.
        {npc_name} must not leave their location.  If the player wants {npc_name} to go somewhere with them, {npc_name} must make up a reason why he/she cannot.""".format(npc_name=self.npc_name)
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt(), #role of any NPC generically
            self._load_fourth_wall(),
            # self._load_scene_objectives(), # the objectives of the scene for the protagonist to meet
            # self._load_npc_in_scene_prompt(), # role of the NPC in the scene (objectives etc)
            self._load_npc_prompt(), # summarization of the NPC (personality etc)
            self._load_knowledge(), #knowledge the NPC is aware of (via tags)
            self._load_long_term_memory(),
            self._load_npc_in_world_prompt(), # role of the NPC in the world
            self._load_conversation_prompt(), # conversation of user with NPC
        ]
        return "\n\n'''''\n".join([fnc for fnc in prompt_assembly_fncs_in_order])

    def _get_system_message_for_knowledge_agent(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt(), #role of any NPC generically
            self._load_fourth_wall(),
            # self._load_scene_objectives(), # the objectives of the scene for the protagonist to meet
            # self._load_npc_in_scene_prompt(), # role of the NPC in the scene (objectives etc)
            self._load_npc_prompt(), # summarization of the NPC (personality etc)
            self._load_npc_in_world_prompt(), # role of the NPC in the world
        ]
        return "\n\n'''''\n".join([fnc for fnc in prompt_assembly_fncs_in_order])

    def _load_generic_npc_prompt(self):
        if self.npc_name == "Narrator":
            generic_npc_prompt = """ROLE: Act like a narrator for this video game.  I, the player, will type messages as a way of interacting with the world.  I want you to respond with what I see, or what happens in the environment around me.  Do not act like a personal AI assistant under any circumstances.  Use your best judgment and further the story (objectives) when you deem fit and respond to the player's queries as a narrator would when you deem fit. I will be the player and seek to achieve the objectives.  For instance, if I say that I am going somewhere, describe the scenery as I pass by.  If I listen for sounds, tell me what I hear.  If another character in the scene does something, describe what that character does in third person.""".format(npc_name=self.npc_name)
        else:
            generic_npc_prompt = """I want you to roleplay as an NPC, {npc_name}, in a video game. {npc_name}'s dialogue adjusts based on their emotional state, showcasing nuances such as sarcasm, humor, or hesitation. Importantly, {npc_name} brings context into their interactions, referencing their knowledge of the world.""".format(npc_name=self.npc_name)
        return generic_npc_prompt
    
    # def _load_npc_in_scene_prompt(self):
    #     '''originally this was a single prompt that is pulled from the front end.  Now this is a scene prompt that is
    #     based off of objective completion as well.'''

    #     #NEW
    #     scene = get_scene(scene_id=self.scene_id)
    #     npc_prompts = [scene['NPCs'][npc]['scene_npc_prompt'] for npc in list(scene['NPCs'])]
    #     npc_prompt = "'''''\n".join(npc_prompts)
        
    #     objectives_prompt = ""
    #     objective_status = get_scene_objectives_status(scene_id=self.scene_id, user_name=self.user_name)
    #     objective_to_status_map = {}
    #     for item in objective_status['completed']:
    #         objective_to_status_map[item] = 'completed'
    #     for item in objective_status['available']:
    #         objective_to_status_map[item] = 'available'
    #     for item in objective_status['unavailable']:
    #         objective_to_status_map[item] = 'unavailable'
    #     # objective_
    #     objectives = scene['objectives']
    #     for objective_set in objectives:
    #         for objective in objective_set:
    #             status = objective_to_status_map[objective['objective']]
    #             if status == 'completed' and 'prompt_completed' in list(objective) and objective['prompt_completed'] != "":
    #                 objectives_prompt += objective['prompt_completed']
    #             elif status == 'available' and 'prompt_available' in list(objective) and objective['prompt_available'] != "":
    #                 objectives_prompt += objective['prompt_available']
    #             elif status == 'unavailable' and 'prompt_unavailable' in list(objective) and objective['prompt_unavailable'] != "":
    #                 objectives_prompt += objective['prompt_unavailable']

    #     prompt = f"""Scene Information:\n
    #     {npc_prompt}\n
    #     {objectives_prompt}\n"""
    #     return prompt

    # def _load_scene_objectives(self):
    #     scene_objectives_status = get_scene_objectives_status(scene_id=self.scene_id, user_name=self.user_name)
    #     # prompt += str(scene_objectives_status['completed'])
    #     prompt = "SCENE OBJECTIVE INFORMATION:\n"
    #     prompt += "scene_objectives = " + str(scene_objectives_status['available'])
    #     prompt += "\n\n"
    #     prompt += '\n'.join([d['prompt_available'] for sublist in self.scene['objectives'] for d in sublist if d['objective'] in scene_objectives_status['available'] and 'prompt_available' in list(d)])
    #     # prompt += str([scene['objectives']scene_objectives_status['available']])
    #     # prompt += "\n\nHere are the unavailable objectives.  These objectives cannot be completed yet.\n"
    #     # prompt += str(scene_objectives_status['unavailable'])


    #     '''Grab personal NPC objectives for a scene as well as generic scene-agnostic NPC objectives/motivations'''
    #     # npc_personal_scene_objectives = "Timmy's personal scene objectives are to forge new friendships and thrive in school, to embody the courage of his superhero idol, and to relish carefree fun without the weight of fear. He aims to rebuild lost confidence, develop trust in others, and conquer the anxiety monster in his dream world, not only empowering himself but also easing his family's worries about his well-being."
    #     # prompt += f"npc_personal_scene_objectives: {npc_personal_scene_objectives}"

    #     return prompt
    

    def _load_npc_in_world_prompt(self):
        world_json = get_world(world_name=self.world_name)
        if 'world_npc_prompt' in world_json:
            world_npc_prompt = world_json['world_npc_prompt']
        elif 'world_description' in world_json:
            world_npc_prompt = world_json['world_description']
        else:
            world_npc_prompt = ""
        if world_npc_prompt == "":
            return ""
        return """GAME INFORMATION:\n {world_npc_prompt}\n\n""".format(world_npc_prompt=world_npc_prompt)
    
    def _load_npc_prompt(self):
        return "" if 'personality' not in list(self.npc) or self.npc['personality'] == "" else f"NPC Personality:\nThe personality of {self.npc_name} is: {self.npc['personality']}"



    def _load_knowledge_via_llamaindex_agent(self):
        
        from KnowledgeBase.knowledge_retriever import LlamaIndexKnowledgeAgent
        knowledge_agent = LlamaIndexKnowledgeAgent(world_name=self.world_name,npc_name=self.npc_name,user_name=self.user_name)
        knowledge = knowledge_agent.method_llamaindex_agent(user_message=self.user_message)
        return knowledge

    def _load_knowledge(self):
        knowledge_from_tags = self._load_knowledge_via_llamaindex_agent()
        knowledge_from_npc = "" if 'knowledge' not in list(self.npc) or self.npc['knowledge'] == "" else self.npc['knowledge']
        knowledge = f"\n\nHere is some game knowledge that {self.npc_name} is aware of:\n{knowledge_from_npc}\n{knowledge_from_tags}"
        return knowledge
    
    def _load_conversation_prompt(self):
        prompt = "Here is the CONVERSATION so far:\n"
        prompt += self.get_conversation()
        return prompt

