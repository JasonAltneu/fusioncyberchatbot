from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.chatbot_service import chatbot_service
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
def chat(message: str):
    """Chat endpoint - uses Gemini API via chatbot service"""
    try:
        response = chatbot_service.chat(message)
        return {"reply": response}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
    

@app.post("/maps")
def maps(message: str):
    """Chat endpoint - uses Google Maps API via chatbot service"""
    try:
        response = chatbot_service.chat(message)
        return {"reply": response}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
