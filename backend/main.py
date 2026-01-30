from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Atlas Financial Assistant",
    description="A GenAI-driven backend for banking/financial queries.",
    version="1.0.0"
)

# CORS Middleware (Allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    from backend.app.agents.graph import app as agent_app
    try:
        # Initial state
        initial_state = {"query": request.query, "messages": []}
        # Run agent
        result = agent_app.invoke(initial_state)
        # Ensure we return a serializable response
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Atlas Financial Assistant is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}



