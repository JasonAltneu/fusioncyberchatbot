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
    initial_prompt: str
    last_updated: str

@dataclass
class Chat:
    id: int
    sender: str
    message: str
    last_updated: str


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
def chat(message: str, chat_id: int = 0):
    """Chat endpoint - uses Gemini API via chatbot service

    The endpoint now supports creating a new conversation when
    `chat_id` is zero.  In that case the initial user message is
    stored in `conversations` and the returned JSON includes the
    new identifier so the frontend can update `activeChat`.

    If a non‑zero `chat_id` is provided, or after a new conversation
    is created, both the user input and bot response are saved in the
    `chat` table as before.
    """
    try:
        # recognize special prefixes for debugging
        lower_msg = message.lower().strip()
        if lower_msg.startswith("map: "):
            print("Received map request")       # Use Google Maps API to find nearby subject
            print(f"{message[5:]}")
        elif lower_msg.startswith("email: "):
            print("Received email request")     # Use MockMail with logging to the console.
            print(f"{message[7:]}")
            response = "I printed the email to the console"
        else:
            response = chatbot_service.chat(message)
            created_id = chat_id

            # if this is a new conversation, insert into conversations table
            if not chat_id or chat_id <= 0:
                try:
                    conn = sqlite3.connect('./chat_history.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO conversations(initial_prompt) VALUES (?)",
                        (message,)
                    )
                    created_id = cursor.lastrowid
                    conn.commit()
                except sqlite3.Error as db_err:
                    print(f"Database creation error: {db_err}")
                finally:
                    if conn:
                        conn.close()

            # now record the chat entries if we have a valid id
        if created_id and created_id > 0:
            try:
                conn = sqlite3.connect('./chat_history.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chat(id, sender, message) VALUES (?, ?, ?)",
                    (created_id, 'user', message)
                )
                cursor.execute(
                    "INSERT INTO chat(id, sender, message) VALUES (?, ?, ?)",
                    (created_id, 'bot', response)
                )
                conn.commit()
            except sqlite3.Error as db_err:
                print(f"Database write error: {db_err}")
            finally:
                if conn:
                    conn.close()

        # return chat_id so frontend can update if new
        result = {"reply": response}
        if created_id and created_id > 0:
            result["chat_id"] = created_id
        return result
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
            SELECT id, initial_prompt, last_updated
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
    
@app.post("/chathistory")
def chathistory(id: str):
    try:
        # Connect to database
        conn = sqlite3.connect('./chat_history.db')
        # Return rows as dictionaries instead of tuples
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Parameterized query (never use string formatting for SQL).
        # explicitly list columns so we know what fields are returned
        query = """
            SELECT id, sender, message, last_updated
            FROM chat
            WHERE id = """+id+"""
            ORDER BY last_updated ASC;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # rows are sqlite3.Row; you can turn them into simple dicts:
        results_dicts = [dict(row) for row in rows]

        # or, if you prefer a typed object with attributes, use our dataclass
        results_objs = [Chat(**dict(row)) for row in rows]

        # FastAPI will happily convert a dataclass to JSON, so either of the
        # following responses is acceptable:
        # return {"names": results_dicts}
        return {"chats": [r.__dict__ for r in results_objs]}

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
