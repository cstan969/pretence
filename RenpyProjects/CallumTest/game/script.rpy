define User = Character("User")
define Callum = Character("Callum", voice='en-us')
define Narrator = Character("Narrator")

image callum_image = "images/callum.jpeg"

init python:
    import api_requests
    class Game:
        def __init__(self):
            print('into game init')
            self.get_renpy_init_state()
            self.final_scene = False

        def get_renpy_init_state(self):
            response = api_requests.get_renpy_init_state()
            self.world_name = response['world_name']
            self.user_name = response['user_name']
            print('world_name: ', self.world_name)
            self.world = api_requests.get_world(world_name=self.world_name)
            print('self.world: ', self.world)

        def get_progress_of_user_in_game(self):
            response = api_requests.get_progress_of_user_in_game(world_name=self.world_name,user_name=self.user_name)
            scene_id = response['scene_id']
            self.scene = api_requests.get_scene(scene_id=scene_id)['scene']
            self.scene_id = self.scene['_id']
            self.npc_name = self.get_npc_in_scene()
            print(self.npc_name)
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

    game = Game()
            


label run_scenes:

    #get the new scene that we're in
    $ game.get_progress_of_user_in_game()

    #setup the background
    show callum_image
    $ renpy.pause(1)
    
    #setup the sprite
    # $ image_filepath = "images/callum.jpeg"
    
    # read the intro narration
    $ intro_narration = game.scene['narration_intro']
    Narrator "[intro_narration]"
    $ game.play_scene_narration_intro()


    #talk to the NPC and fulfill the objectives 
    $ user_input = None
    while True:
        $ user_input = renpy.input("Enter your message: ")
        User "[user_input]"

        if user_input is not None and user_input != "":
            $ response, scene_completed = game.message_npc_and_get_response(user_input)
            Callum "[response]"
            $ game.npc_text_to_speech(response)
            if scene_completed:
                $ outro_narration = game.scene['narration_outro']
                Narrator "[outro_narration]"
                $ game.play_scene_narration_outro()
                if game.final_scene:
                    return
                else:
                    call run_scenes


label start:
    #intro game narration
    $ intro_narration = game.world['narration_intro']
    Narrator "[intro_narration]"
    $ game.play_world_narration_intro()
    call run_scenes
    $ outro_narration = game.world['narration_outro']
    Narrator "[outro_narration]"
    $ game.play_world_narration_outro()

    return
