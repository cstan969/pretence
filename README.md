# pretence

  USE_4BIT=false && USE_13B_MODEL=true && uvicorn servers.vicuna_server:app

  uvicorn VicunaNpcUserInteractionAPI:app --reload --port 8001
  
  uvicorn mongo_api:app --reload --port 8002
  
  uvicorn GameDesignerAIAPI:app --reload --port 8003
  
  uvicorn ExtractorAPI:app --reload --port 8004
