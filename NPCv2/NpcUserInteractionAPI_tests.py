import requests
import json

base_url = 'http://localhost:8001'  # Assuming the FastAPI server is running locally on port 8000



from mongodb.mongo_fncs import get_formatted_conversational_chain

# convo = get_formatted_conversational_chain(world_name='TraumaGame',user_name='Carl',npc_name="Callum")
# print(convo)

# Now test the /message_npc endpoint
npc_user_interaction = {
    "npc_name": "Callum",
    "user_name": "Carl",
    "world_name": "TraumaGame",
    "user_message": "Hello there, how are you today?"
}


# response = requests.post(f"{base_url}/message_npc_and_get_response", json=npc_user_interaction)
# # Again, assuming the server returns a JSON response, print the response
# if response.status_code == 200:
#     print('NPC Response:\n', response.json()['response'])
# else:
#     print(f"Request failed with status {response.status_code}")