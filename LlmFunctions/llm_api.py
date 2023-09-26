# from fastapi import FastAPI
# import llm_functions as fncs
# import uvicorn
# from fastapi.middleware.cors import CORSMiddleware
# import pprint
# import shutil

# from config import API_CORS_ORIGINS

# app = FastAPI()
# origins = API_CORS_ORIGINS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# @app.post("/genMemoriesFromBackstory")
# async def genMemoriesFromBackstory(q:dict):
#     return fncs.genMemoriesFromBackstory(backstory=q['backstory'])