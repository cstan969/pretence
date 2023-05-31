import requests
import json

base_url = 'http://localhost:8001'  # Assuming the FastAPI server is running locally on port 8000

# Define the user and NPC
npc_user_interaction = {
    "npc_name": "Captain Valeria",
    "user_name": "Carl"
}
# Test the /conversation endpoint
response = requests.post(f"{base_url}/get_conversation", json=npc_user_interaction)
# Assuming the server returns a JSON response, print the conversation
if response.status_code == 200:
    print('Conversation:\n', response.json()['conversation'])
else:
    print(f"Request failed with status {response.status_code}")






# Now test the /message_npc endpoint
npc_user_interaction = {
    "npc_name": "Captain Valeria",
    "user_name": "Carl",
    "user_message": "Hello Valeria, how are you today?"
}
response = requests.post(f"{base_url}/message_npc_and_get_response", json=npc_user_interaction)
# Again, assuming the server returns a JSON response, print the response
if response.status_code == 200:
    print('NPC Response:\n', response.json()['response'])
else:
    print(f"Request failed with status {response.status_code}")