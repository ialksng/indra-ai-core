from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from core.brain import chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: str = "lite"
    agent: bool = False

@app.get("/")
def root():
    return {"status": "Indra AI running"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    return chat(req.user_id, req.message, req.mode, req.agent)