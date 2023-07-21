from NpcUserInteraction import NpcUserInteraction
from mongodb.mongo_fncs import *


# convo = get_formatted_conversational_chain(world_name='TraumaGame',user_name='Carl',npc_name='Callum')
# print(convo)

# interaction = NpcUserInteraction(
#     world_name='NocturnalVeil',
#     scene_id='scenes-NocturnalVeil-07112023093300',
#     npc_name='Forensic Detective',
#     user_name='Carl'
#     )

interaction = NpcUserInteraction(
    world_name='TraumaGame',
    scene_id='scenes-TraumaGame-20230711145400',
    npc_name='Callum',
    user_name='Carl3'
    )
output = interaction._get_prompt()
print(output)
# interaction.message_npc_and_get_response(user_message='hello there how are you doing today?')