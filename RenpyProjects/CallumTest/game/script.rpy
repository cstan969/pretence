define User = Character("User")
default NPCNAME = "Callum"
define NPC = Character("[NPCNAME]", voice='en-us')
define Narrator = Character("Narrator", what_slow_cps=30)

#Dynamic Variables
default scene_image_default = "TraumaGame/callum.jpeg"
image scene_image = "[scene_image_default]"
image top_right_text = ParameterizedText(xalign=0.98,yalign=0.0)

init python:
    import api_requests
    import os
    import shutil
    PRETENCE_PATH = os.getenv('PRETENCE_PATH')
    class Game:
        def __init__(self):
            self.get_renpy_init_state()
            self.final_scene = False
            self.background_image_filepath = ""
            self.music_filpath = ""

        def get_renpy_init_state(self):
            response = api_requests.get_renpy_init_state()
            self.world_name = response['world_name']
            self.user_name = response['user_name']
            self.world = api_requests.get_world(world_name=self.world_name)

        def get_progress_of_user_in_game(self):
            response = api_requests.get_progress_of_user_in_game(world_name=self.world_name,user_name=self.user_name)
            scene_id = response['scene_id']
            self.scene = api_requests.get_scene(scene_id=scene_id)['scene']
            print('self.scene: ', self.scene)
            self.scene_id = self.scene['_id']
            self.npc_name = self.get_npc_in_scene()
            print('NPCNAME: ', NPCNAME)
            return self.scene

        def get_npc_in_scene(self):
            #for now it just returns the first NPC because we're locking to one NPC
            npc = list(self.scene['NPCs'])[0]
            return npc

        def get_next_scene(self):
            pass

        def message_npc_and_get_response(self, user_message):
            response = api_requests.message_npc_and_get_response(
                world_name=self.world_name,
                user_name=self.user_name,
                user_message=user_message,
                scene_id=self.scene_id,
                npc_name=self.npc_name
            )
            npc_response = response['npc_response']
            scene_completed = response['scene_completed']
            print(npc_response)
            print(scene_completed)
            return npc_response, scene_completed

        def npc_text_to_speech(self, npc_message):
            api_requests.npc_text_to_speech(npc_message)

        def play_scene_narration_intro(self):
            print('into play_narration_intro')
            if 'narration_intro' in self.scene:
                print('narration_intro in self.scene')
                print(self.scene['narration_intro'])
                api_requests.npc_text_to_speech(self.scene['narration_intro'])

        def play_scene_narration_outro(self):
            print(self.scene)
            if 'narration_outro' in self.scene:
                api_requests.npc_text_to_speech(self.scene['narration_outro'])
        
        def play_world_narration_intro(self):
            print('into world narration intro')
            print(self.world)
            if 'narration_intro' in self.world:
                api_requests.npc_text_to_speech(self.world['narration_intro'])

        def play_world_narration_outro(self):
            print('into world narration outro')
            print(self.world)
            if 'narration_outro' in self.world:
                api_requests.npc_text_to_speech(self.world['narration_outro'])

        def get_scene_objectives_status(self):
            objective_status = api_requests.get_scene_objectives_status(scene_id=self.scene_id, user_name=self.user_name)
            lines = ["--{s}" + o + "{/s}" for o in objective_status['completed']]
            # lines.extend(["--" + o for o in objective_status['available']])
            display_text = '\n'.join(lines)
            return display_text

    game = Game()

            


label run_scenes:
    #get the new scene that we're in
    $ game.get_progress_of_user_in_game()


    # $ music = game.music_filepath
    if 'background_image_filepath' in game.scene and game.scene['background_image_filepath'] != "":
        $ scene_image_default = game.scene['background_image_filepath']
        show scene_image

    if 'music_filepath' in game.scene and game.scene['music_filepath'] != '':
        $ music_path = game.scene['music_filepath']
        play music music_path

    $ renpy.pause(1)
    $ objective_txt = game.get_scene_objectives_status()
    show top_right_text "[objective_txt]"

    
    #setup the sprite
    # $ image_filepath = "images/callum.jpeg"
    
    # read the intro narration
    if 'narration_intro' in game.scene:
        $ intro_narration = game.scene['narration_intro']
        Narrator "[intro_narration]"
        # $ game.play_scene_narration_intro()
        


    #talk to the NPC and fulfill the objectives 
    $ user_input = None
    while True:
        $ user_input = renpy.input("Enter your message: ")
        User "[user_input]{nw}"

        if user_input is not None and user_input != "":
            $ response, scene_completed = game.message_npc_and_get_response(user_input)
            $ NPCNAME = game.npc_name
            NPC "[response]"
            # $ game.npc_text_to_speech(response)
            $ objective_txt = game.get_scene_objectives_status()
            show top_right_text "[objective_txt]"
            if scene_completed:
                $ renpy.pause(5)
                $ outro_narration = game.scene['narration_outro']
                Narrator "[outro_narration]"
                # $ game.play_scene_narration_outro()
                if game.final_scene:
                    return
                else:
                    call run_scenes


label start:
    #intro game narration
    #ADD GAME INTRO BACKGROUND
    # if 'narration_intro' in game.world:
    #     $ intro_narration = game.world['narration_intro']
    #     $ renpy.pause(1)
    #     # Narrator "[intro_narration]"
    #     $ game.play_world_narration_intro()
    call run_scenes
    #outro game narration
    if 'narration_outro' in game.world:
        $ outro_narration = game.world['narration_outro']
        # Narrator "[outro_narration]"
        $ game.play_world_narration_outro()

    return
