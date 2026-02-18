from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from services.chatbot_service import chatbot_service, ChatbotService
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Fusion Cyber Chatbot API",
    description="Backend API for the Fusion Cyber Chatbot",
    version="0.1.0"
)

# Configure CORS for frontend communication
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint - health check"""
    return {"message": "Fusion Cyber Chatbot API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/chat")
def chat(message: str, session_id: Optional[str] = None):
    """Chat endpoint - uses Gemini API via chatbot service.

    A session_id may be provided so that history is persisted for that
    conversation; if omitted the global singleton is used.
    """
    try:
        # if a session_id is provided, create a temporary service for it so
        # the history can be fetched/stored independently of the singleton.
        if session_id:
            svc = ChatbotService(session_id=session_id)
            response = svc.chat(message)
        else:
            response = chatbot_service.chat(message)
        return {"reply": response}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

@app.post("/maps")
def maps(message: str):
    """Chat endpoint - uses Google API via chatbot service"""
    try:
        response = chatbot_service.chat(message)
        return {"reply": response}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}


@app.get("/history")
def get_history(session_id: Optional[str] = None):
    """Return the conversation history for the given session (or global)."""
    if session_id:
        svc = ChatbotService(session_id=session_id)
        return {"history": svc.get_conversation_history()}
    return {"history": chatbot_service.get_conversation_history()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
