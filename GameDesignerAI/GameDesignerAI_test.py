import os
from GameDesignerAI import GameDesignerAI

class GameDesignerAITests():

            
    def test_get_conversation(self):
        print('---test_get_conversation---')
        gdai = GameDesignerAI('test_world_name')
        return gdai.get_conversation()
    

    def test_message_game_designer_ai_and_get_response(self):
        print('---test_message_game_designer_ai_and_get_response---')
        gdai=GameDesignerAI('test_world_name')
        # user_message="Can you create an NPC for me.  I want that NPC to be named Biblo Baggins.  I want Bilbo to be angry and paranoid.  Bilbo wants you to bring him food and snacks no matter what.  He will have you go on dangerous quests to find some of the most delicious ingredients for him and then cook meals for him."
        # user_message="Can you create a first queste and objectives that Bilbo might give me please?"
        user_message = "that sounds great but I also want the quest to be dangerous.  Are they mushroom monsters? or are they guarded by monsters?  Or are the mushrooms poisonous and difficult to cook with?  Or maybe all of the above?"
        return gdai.message_game_designer_ai_and_get_response(user_message=user_message)
    
    def test__get_prompt(self):
        pass

    def test_load_generic_game_designer_ai_prompt(self):
        print('---test_load_generic_game_designer_ai_prompt---')
        gdai = GameDesignerAI('test_world_name')
        return gdai._load_generic_game_designer_ai_prompt()

gdait = GameDesignerAITests()
print(gdait.test_load_generic_game_designer_ai_prompt())
print(gdait.test_get_conversation())
print(gdait.test_message_game_designer_ai_and_get_response())