define u = Character("User")
define Callum = Character("Callum", voice='en-us')

image callum_image = "images/callum.jpeg"

init python:
    import api_requests
    class Game:
        def __init__(self):
            self.world_name = 'NocturnalVeil'
            # self.world_name='TraumaGame'
            self.user_name = 'Carl5'
            # self.scene_id = 'scenes-NocturnalVeil-07112023093300'
            # self.scene_id = 'scenes-TraumaGame-20230711145400' #self.current_scene()
            # self.npc_name = 'Callum' #self.get_npc_in_scene()
            # self.npc_name = self.get_npc_in_scene()
            # self.npc_name = 'Forensic Detective'

        def get_progress_of_user_in_game(self):
            response = api_requests.get_progress_of_user_in_game(world_name=self.world_name,user_name=self.user_name)
            scene_id = response['scene_id']
            self.scene = api_requests.get_scene(scene_id=scene_id)['scene']
            self.scene_id = self.scene['_id']
            self.npc_name = self.get_npc_in_scene()
            return self.scene

        def get_npc_in_scene(self):
            npc = list(self.scene['NPCs'])[0]
            print('npc: ', npc)
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

        def play_narration_intro(self):
            print('into play_narration_intro')
            if 'narration_intro' in self.scene:
                print('narration_intro in self.scene')
                print(self.scene['narration_intro'])
                api_requests.npc_text_to_speech(self.scene['narration_intro'])

        def play_narration_outro(self):
            print(self.scene)
            if 'narration_outro' in self.scene:
                api_requests.npc_text_to_speech(self.scene['narration_outro'])
    

            
label start:

    #Initialize the game and get the scene that the user is on
    $ game = Game()
    
    #get the new scene that we're in
    $ game.get_progress_of_user_in_game()

    #setup the background
    show callum_image
    $ renpy.pause(1)
    
    #setup the sprite
    # $ image_filepath = "images/callum.jpeg"
    
    # read the intro narration
    $ game.play_narration_intro()

    #talk to the NPC and fulfill the objectives 
    $ user_input = None
    while True:
        $ user_input = renpy.input("Enter your message: ")

        if user_input is not None and user_input != "":
            $ response, scene_completed = game.message_npc_and_get_response(user_input)
            Callum "[response]"
            $ game.npc_text_to_speech(response)
            if scene_completed:
                $ game.play_narration_outro()
                jump start


