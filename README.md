# pretence

uvicorn VicunaNpcUserInteractionAPI:app --reload --port 8001
uvicorn mongo_api:app --reload --port 8002
uvicorn GameDesignerAIAPI:app --reload --port 8003
uvicorn ExtractorAPI:app --reload --port 8004
