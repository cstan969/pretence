from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from Extractor import Extractor


app = FastAPI()
origins = [
    "http://localhost:5173",
    "localhost:5173",
    "http://127.0.0.1:5173",
    "127.0.0.1:6173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/extract_all')
async def extract_all(q:dict):
    world_name=q['world_name']
    ext = Extractor(world_name=world_name)
    ext.extract_all()
    return {'extractions': ext}