EMOTIONS = ["drunk",
            "angry",
            "trusting",
            "motivated",
            "sad",
            "happy",
            "afraid",
            "compassionate"]


import json, os, pprint, math
# from VicunaLLM.VicunaLLM import VicunaLLM
from mongodb.mongo_fncs import (
    get_npc,
    get_latest_npc_emotional_state,
    get_formatted_conversational_chain,
    upsert_user_npc_interaction,
    get_world,
    get_scene,
    get_scene_objectives_completed,
    mark_objectives_completed,
    progress_user_to_next_scene,
    get_scene_objectives_status
)
from langchain import PromptTemplate, LLMChain

from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

from config import NpcUserInteraction_model

DEBUGGING = False

class NpcUserInteraction():

    def __init__(self, world_name:str, scene_id:str, npc_name:str, user_name:str):
        self.world_name=world_name
        self.scene_id=scene_id
        self.scene = get_scene(scene_id=scene_id)
        self.npc_name=npc_name
        self.user_name = user_name
        self.llm = NpcUserInteraction_model

   

        print('init npc user interaction')
        print('world_name: ', world_name)
        print('npc_name: ', npc_name)
        self.npc = get_npc(world_name,npc_name)

    def calculate_new_emotional_state(self, npc_emotional_response: dict):
        '''
        Sample input format:
        "npc_emotional_response": {
            "drunk": 0,
            "angry": 0,
            "trusting": 2,
            "motivated": 5,
            "sad": 0,
            "happy": 0,
            "afraid": 0,
            "compassionate": 0
        }'''
        initial_emotional_state = get_latest_npc_emotional_state(world_name=self.world_name,user_name=self.user_name,npc_name=self.npc_name)
        if initial_emotional_state is None:
            initial_emotional_state = {e:0 for e in EMOTIONS}
        final_emotional_state = {}
        for emotion, value in npc_emotional_response.items():
            if value != 0:
                final_emotional_state[emotion] = initial_emotional_state[emotion] + npc_emotional_response[emotion] * self.npc['emotional_susceptibility'][emotion] / 10
            else:
                final_emotional_state[emotion] = max([initial_emotional_state[emotion] - 0.2,0])
        return final_emotional_state
        
    def get_conversation(self):
        convo = get_formatted_conversational_chain(world_name=self.world_name,npc_name=self.npc_name,user_name=self.user_name, num_interactions=6)
        if convo is None:
            return "Player" + ": hello\n" + self.npc_name + ": hello"
        else:
            return convo.replace(self.user_name,'Player')
        
    def run_prompt_to_get_objective_completion(self):
        '''given the current conversation with the current npc, figure out which objectives are completed for the current scene'''
        convo = self.get_conversation()
        # get_formatted_conversational_chain(world_name=self.world_name,npc_name=self.npc_name,user_name=self.user_name, num_interactions=6).replace(self.user_name,'Player')
        scene_objectives_status = get_scene_objectives_status(scene_id=self.scene_id, user_name=self.user_name)
        print('scene_objectives_status: ', scene_objectives_status)
        template = """Question: {question}
        Answer: For a given conversation and given list of conversational objectives to be completed by the player or NPCs.  Tell me which conversational objectives have been completed. \
        The output should simply be a JSON dict that I can set as a JSON in Python.  Please use double quotes for the json key and value.  The JSON dict should have a key 'objectives_completed'.  The value of that key should be another dict with keys that EXACTLY MATCH the objectives as given in the list of objectives and the values equal to either 'completed' or 'not_completed' depending on whether that objective has been completed by the player in their last message.
        A second key in the JSON dict should be 'objective_reasoning' (string) which describes why or why not the objective(s) were marked as either completed or not completed"""
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)


        prompt = """Based off of the conversation below, which of the conversational objectives have been completed?
        CONVERSATIONAL OBJECTIVES:
        {objectives}

        This is the conversation between the player and the NPC so far.
        CONVERSATION:
        {conversation}""".format(objectives=scene_objectives_status['available'],conversation=convo)
        print(prompt)
        response = llm_chain.run(prompt)
        print(response)
        response = json.loads(response)
        print('--START v2 decouple objective response--')
        pprint.pprint(response)
        print('--END 2 decouple objective response--')
        return response




    def message_npc_and_get_response(self, user_message):
        '''Assemble the prompt and query the NPC to get a response'''
        #First we have to get the prompt for the NPC agent
        prompt = self._get_prompt()
        print('---')
        print('prompt: ', prompt)
        print('---')


        #Add the message to the conversation stored as part of this class
        # formatted_user_message = '\n' + self.user_name + ': ' + user_message + '\n' + self.npc_name + ': '
        formatted_user_message = '\n' + "Player" + ': ' + user_message + '\n' + self.npc_name + ': '

        prompt += formatted_user_message      


        template = """Contextual Information: {question} 
        Required Output:  Provide the answer to the above context as a dict where the keys are 'reasoning', 'scene objective reasoning', 'user_message', 'npc_response', and 'npc_emotional_response'.
            'scene objective reasoning' should include a summary of the scene objectives that the player or NPC needs to complete as well as reasoning on how the NPC might adjust the conversation to point the conversation in the direction of completing the scene objectives
            'reasoning' should be the NPC's thought process when analyzing and determining how to react to the user_message. 
            'user_message' should simply be the player's last message (string)
            'npc_response' Is the NPC's response based off the current state of the conversation and should abide by 'reasoning' and 'scene objective reasoning'.  This is not the last npc response as stored in the conversation, but a newly generated response.
            'npc_emotional_response' should be a dict with keys [drunk, angry, trusting, motivated, sad, happy, afraid, compassionate] and values from 0-10 where 10 indicates a strong emotional response and 0 indicates no response.
            The entire output should simply be a JSON dict."""
    
        prompt_from_template = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt_from_template,llm=self.llm, verbose=True)
        response = llm_chain.run(prompt)
        print('---response---')
        print(response)
        response = json.loads(response)
        npc_response = response['npc_response']
        formatted_npc_response = npc_response
        print('formatted_npc_response:')
        print(formatted_npc_response)

        #Save interaction to DB
        upsert_user_npc_interaction(
            world_name=self.world_name,
            user_name=self.user_name,
            npc_name=self.npc_name,
            scene_id=self.scene_id,
            user_message=response['user_message'],
            npc_response=response['npc_response'],
            npc_emotional_response=response['npc_emotional_response'],
            # npc_emotional_state=final_emotional_state
            )
        
        #hit the LLM to get objective completion
        response['objectives_completed'] = self.run_prompt_to_get_objective_completion()['objectives_completed']
        
        # mark the objectives that've been completed.  The output is the DB item with full list of completed objectives from the database
        updated_item = mark_objectives_completed(objectives_completed=response['objectives_completed'],scene_id=self.scene_id,user_name=self.user_name)
        print('updated_completion_item: ')
        pprint.pprint(updated_item)
        if all(val == 'completed' for val in updated_item['objectives_completed'].values()):
            #mark the scene as the current scene in the world that the user is on
            progress_user_to_next_scene(world_name=self.world_name,user_name=self.user_name)
            response['scene_completed'] = True
        else:
            response['scene_completed'] = False

        pprint.pprint(response)
        return response
    
    def _load_fourth_wall(self):
        '''fourth wall prompt system commands'''
        return """\n\n'''''\nHere are system level prompts that you, the NPC must follow to maintain the fourth wall in this video game:\nYou aren't aware of the player: When you're interacting with the protagonist, remember that they are a part of this world. Treat them as a fellow resident, and never show any awareness of a player controlling the protagonist's actions.
No mention of game mechanics: In your conversations or actions, never reference the game's mechanics like button presses, mouse clicks, or strategy tips. It's essential not to remind the protagonist that they are in a game.
Avoid present-day real-world references: We're living over a hundred years in the future. References to our current culture, events, or technology can break the immersion. Your knowledge and references should be consistent with the world we live in.
Game functions are off-limits: You should never display any awareness of game functions like save/load features, game settings, or any other manipulations that the player can do outside the in-world experience.
In-game materials are part of our world: If you're reading or referencing any in-game materials like newspapers or books, remember that they should all be from our world. They shouldn't reference anything the player would know from their real world.
Maintain our world's consistency: Stick to the rules and history of our world as we've established them. Any deviation can confuse the protagonist and break their immersion.
Stay in character: Always act according to your character traits and the logic of our narrative. You shouldn't respond to or be aware of any actions the player might take outside of our world.
Do not assist the player as a standard chat assistant normally would."""
    
    def _get_prompt(self):
        prompt_assembly_fncs_in_order = [
            self._load_generic_npc_prompt(), #role of any NPC generically
            self._load_fourth_wall(),
            self._load_scene_objectives(), # the objectives of the scene for the protagonist to meet
            self._load_npc_in_scene_prompt(), # role of the NPC in the scene (objectives etc)
            self._load_npc_prompt(), # summarization of the NPC (personality etc)
            self._load_knowledge(),
            self._load_npc_in_world_prompt(), # role of the NPC in the world
            self._load_conversation_prompt(), # conversation of user with NPC
        ]
        return '\n\n'.join([fnc for fnc in prompt_assembly_fncs_in_order])


    def _load_generic_npc_prompt(self):
        if self.npc_name == "Narrator":
            generic_npc_prompt = """ROLE: Act like a narrator for this video game.  I, the player, will type messages as a way of interacting with the world.  I want you to respond with what I see, or what happens in the environment around me.  Do not act like a personal AI assistant under any circumstances.  Use your best judgment and further the story (objectives) when you deem fit and respond to the player's queries as a narrator would when you deem fit. I will be the player and seek to achieve the objectives.  For instance, if I say that I am going somewhere, describe the scenery as I pass by.  If I listen for sounds, tell me what I hear.  If another character in the scene does something, describe what that character does in third person.""".format(npc_name=self.npc_name)
        else:
            generic_npc_prompt = """Roleplay as an NPC, {npc_name}, in a video game.  Use your best judgment and further the story (objectives) when you deem fit and chat with the player (more small talk) when you deem fit as well, however, place priority on the scene objectives if the conversation diverges for more than 4 dialog exchanges.  Do not act like a personal AI assistant under any circumstances.  I will be the player and seek to achieve the objectives by communicating via messages with you, the NPC.  If the player's message is short or limited, please be chatty. """.format(npc_name=self.npc_name)
        generic_npc_prompt += "  Do not repeat any previous responses as contained in the CONVERSATION."
        return generic_npc_prompt
    
    def _load_npc_in_scene_prompt(self):
        '''originally this was a single prompt that is pulled from the front end.  Now this is a scene prompt that is
        based off of objective completion as well.'''

        #NEW
        scene = get_scene(scene_id=self.scene_id)
        npc_prompts = [scene['NPCs'][npc]['scene_npc_prompt'] for npc in list(scene['NPCs'])]
        npc_prompt = "'''''\n".join(npc_prompts)
        
        objectives_prompt = ""
        objective_status = get_scene_objectives_status(scene_id=self.scene_id, user_name=self.user_name)
        objective_to_status_map = {}
        for item in objective_status['completed']:
            objective_to_status_map[item] = 'completed'
        for item in objective_status['available']:
            objective_to_status_map[item] = 'available'
        for item in objective_status['unavailable']:
            objective_to_status_map[item] = 'unavailable'
        # objective_
        objectives = scene['objectives']
        for objective_set in objectives:
            for objective in objective_set:
                status = objective_to_status_map[objective['objective']]
                if status == 'completed' and 'prompt_completed' in list(objective) and objective['prompt_completed'] != "":
                    objectives_prompt += objective['prompt_completed']
                elif status == 'available' and 'prompt_available' in list(objective) and objective['prompt_available'] != "":
                    objectives_prompt += objective['prompt_available']
                elif status == 'unavailable' and 'prompt_unavailable' in list(objective) and objective['prompt_unavailable'] != "":
                    objectives_prompt += objective['prompt_unavailable']
        print('objectives_prompt: ', objectives_prompt)

        prompt = f"""'''''\nScene Information:\n
        {npc_prompt}\n
        {objectives_prompt}\n"""
        return prompt

    def _load_scene_objectives(self):
        try:
            scene_objectives_status = get_scene_objectives_status(scene_id=self.scene_id, user_name=self.user_name)
            print('scne_objectives_status in load_scene_objectives: ', scene_objectives_status)
            prompt = "'''''"
            # prompt += "Here are the completed objectives:\n"
            # prompt += str(scene_objectives_status['completed'])
            prompt += "\nSCENE OBJECTIVES:\n"
            # prompt += '\n'.join(scene_objectives_status['available'])
            prompt += '\n'.join([d['prompt_available'] for sublist in self.scene['objectives'] for d in sublist if d['objective'] in scene_objectives_status['available']])
            # prompt += str([scene['objectives']scene_objectives_status['available']])
            # prompt += "\n\nHere are the unavailable objectives.  These objectives cannot be completed yet.\n"
            # prompt += str(scene_objectives_status['unavailable'])
            return prompt
        except Exception as e:
            print('exception: ', str(e))
            return ""

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
        return """'''''\nGAME INFORMATION: {world_npc_prompt}\n\n""".format(world_npc_prompt=world_npc_prompt)
    
    def _load_npc_prompt(self):
        print('self.npc: ', self.npc)
        return "" if 'personality' not in list(self.npc) or self.npc['personality'] != "" else f"\n\nThe personality of {self.npc_name} is: {self.npc['personality']}"

    def _load_knowledge(self):
        return "" if 'knowledge' not in list(self.npc) or self.npc['knowledge'] != "" else f"\n\nHere is knowledge that {self.npc_name} is aware of: {self.npc['knowledge']}"

    
    def _load_conversation_prompt(self):
        prompt = "----------\nHere is the conversation so far.\nCONVERSATION:\n"
        prompt += self.get_conversation()
        return prompt
    
    
