import requests
import os

world_name='TraumaGame'
user_name='Carl3'
scene_id="scenes-TraumaGame-20230711145400"

base_url = 'http://localhost:8001'
def message_npc_and_get_response(user_input):
    # npc_user_interaction = {
    #     'world_name': 'NocturnalVeil',
    #     'scene_id': 'scenes-NocturnalVeil-07112023093300',
    #     "npc_name": "Forensic Detective",
    #     "user_name": "Carl",
    #     "user_message": user_input
    # }

    npc_user_interaction = {
        'world_name': world_name,
        'scene_id': 'scenes-TraumaGame-20230711145400',
        "npc_name": "Callum",
        "user_name": user_name,
        "user_message": user_input
    }

    response = requests.post(f"{base_url}/message_npc_and_get_response", json=npc_user_interaction)
    return response.json()

def npc_text_to_speech(user_input):
    # os.system("source ~/Pretence/TTS/mimic3/venv/bin/activate && mimic3 --remote --voice 'en_UK/apope_low' 'My hovercraft is full of eels.'")
    response = requests.post('http://localhost:8005/TTS',json={'text':user_input})
    return response.json()

def get_progress_of_user_in_game(world_name: str, user_name: str):
    '''given a world name, get the progress (e.g. scene_id) of the user_name in that world'''
    response = requests.get('http://localhost:8002/get_progress_of_user_in_game',json={'world_name':world_name,'user_name':user_name})
    return response.json()

def get_scene(scene_id: str):
    '''grab the dictionary scene document given the scene_id'''
    response = requests.get('http://localhost:8002/get_scene',json={'scene_id': scene_id})
    return response.json()