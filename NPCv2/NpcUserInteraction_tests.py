from NpcUserInteraction_v2 import NpcUserInteraction
from mongodb.mongo_fncs import *


# convo = get_formatted_conversational_chain(world_name='TraumaGame',user_name='Carl',npc_name='Callum')
# print(convo)

# interaction = NpcUserInteraction(
#     world_name='NocturnalVeil',
#     scene_id='scenes-NocturnalVeil-07112023093300',
#     npc_name='Forensic Detective',
#     user_name='Carl'
#     )

def test_get_prompt():
    interaction = NpcUserInteraction(
        world_name='TraumaGame',
        scene_id='scenes-TraumaGame-20230711145400',
        npc_name='Callum',
        user_name='Carl3'
        )
    output = interaction._get_prompt()
    print(output)

def test_get_speech_pattern():
    interaction = NpcUserInteraction(world_name='Dreambound',scene_id='scenes-Dreambound-20230726193433827682',user_name='James Thomas Stanhope',npc_name='Little Timmy')
    speech_pattern = interaction._get_speech_pattern(npc_emotional_state={
        "Happiness": 3,
        "Sadness": 6,
        "Anger": 0,
        "Fear": 8,
        "Surprise": 5,
        "Disgust": 0,
        "Excitement": 4,
        "Confusion": 7,
        "Calmness": 2,
        "Curiosity": 5,
        "Pride": 2,
        "Shyness": 7
    })
    print(speech_pattern)

test_get_speech_pattern()

# interaction.message_npc_and_get_response(user_message='hello there how are you doing today?')