from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.chatbot_service import chatbot_service
from dotenv import load_dotenv
import sqlite3
from dataclasses import dataclass

# simple typed container for the conversation table
@dataclass
class Conversation:
    id: int
    session_id: str
    initial_prompt: str


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

@app.post("/history")
def getHistory():
    try:
        # Connect to database
        conn = sqlite3.connect('./chat_history.db')

        # Return rows as dictionaries instead of tuples
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        # Parameterized query (never use string formatting for SQL).
        # explicitly list columns so we know what fields are returned
        query = """
            SELECT id, session_id, initial_prompt
            FROM conversations
            ORDER BY id ASC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # rows are sqlite3.Row; you can turn them into simple dicts:
        results_dicts = [dict(row) for row in rows]

        # or, if you prefer a typed object with attributes, use our dataclass
        results_objs = [Conversation(**dict(row)) for row in rows]

        # FastAPI will happily convert a dataclass to JSON, so either of the
        # following responses is acceptable:
        # return {"names": results_dicts}
        return {"names": [r.__dict__ for r in results_objs]}

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        if conn:
            conn.close()
    

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
