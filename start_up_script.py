from config import port_allocations


#NpcUserInteraction API
uvicorn NpcUserInteractionAPI:app --reload --port 8001

uvicorn GameDesignerAIAPI:app --reload --port 8003
uvicorn ExtractorAPI:app --reload --port 8004





# # NpcUserInteractionAPI
# COMMAND="""source ~/Pretence/venv/bin/activate && uvicorn ~/Pretence/NpcUserInteraction/NpcUserInteractionAPI:app --reload --port {port}""".format(port=port_allocations['NpcUserInteractionAPI'])
# import subprocess


# # Number of terminal windows to open
# NUM_WINDOWS = 1

# for i in range(1, NUM_WINDOWS + 1):
#     subprocess.Popen(['gnome-terminal', '--tab', '--title=API Window {}'.format(i), '--command={}'.format(COMMAND)])
