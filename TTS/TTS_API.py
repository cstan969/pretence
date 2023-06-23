from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os


app = FastAPI()
origins = [
    "http://localhost:5173",
    "localhost:5173",
    "http://127.0.0.1:5173",
    "127.0.0.1:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/TTS")
async def text_to_speech(q: dict)->dict:
    print(q)
    text = q['text']
    os.system("""mimic3 --remote --voice 'en_UK/apope_low' \"{text}\"""".format(text=text))
    return {}


from config import port_allocations
if __name__ == '__main__':
    uvicorn.run(app,host='127.0.0.1', port=port_allocations['TTSAPI'])
