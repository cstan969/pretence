import requests
from unittest import TestCase
from GameDesignerAI import GameDesignerAI

base_url='http://localhost:8003'

class GameDesignerAIAPITests(TestCase):

    def test_extract(self):
        pass

    def test_get_conversation(self):
        print('---test_get_conversation---')
        response = requests.get(f"{base_url}/get_conversation", json={'world_name':'test_world_name'})
        if response.status_code == 200:
            print(response.json())
            print('Conversation:\n', response.json()['conversation'])
        else:
            print(f"Request failed with status {response.status_code}")

    def test_message_game_designer_ai_and_get_response(self):
        print('---test_message_game_designer_ai_and_get_response---')
        request_payload={
            'world_name':'test_world_name',
            'user_message':'are there any characters already made?'
        }
        response = requests.post(f"{base_url}/message_game_designer_ai_and_get_response", json=request_payload)
        if response.status_code == 200:
            print(response.json())
            print('Response:\n', response.json()['response'])
        else:
            print(f"Request failed with status {response.status_code}")

tc = GameDesignerAIAPITests()
# tc.test_get_conversation()
tc.test_message_game_designer_ai_and_get_response()