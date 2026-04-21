from fastapi import FastAPI
from pydantic import BaseModel
from core.brain import chat

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    result = chat(req.user_id, req.message)
    return result

@app.get("/")
def root():
    return {"status": "Indra AI running"}

@app.get("/ping")
def ping():
    return {"status": "alive"}