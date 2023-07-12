# pretence

  Add PRETENCE_PATH to your .bashrc or window path etc.

  USE_4BIT=false && USE_13B_MODEL=true && uvicorn servers.vicuna_server:app

  uvicorn NpcUserInteractionAPI:app --reload --port 8001
  
  uvicorn mongo_api:app --reload --port 8002
  
  uvicorn GameDesignerAIAPI:app --reload --port 8003
  
  uvicorn ExtractorAPI:app --reload --port 8004

  run GameDesignerSuite via ~/Pretence/pretence-app-2/pretence_frontend/src pnpm run dev

  run mimic3 server via source ~/Pretence/TTS/venv/bin/activate && mimic3-server --cuda which run on http://0.0.0.0:59125

  run TTS_API.py via uvicorn ~/Pretence/TTS/TTS_API:app --reload --port 8005

  
