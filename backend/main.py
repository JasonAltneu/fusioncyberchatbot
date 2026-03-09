from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.chatbot_service import chatbot_service
from services.maps_service import map_service
from dotenv import load_dotenv
import sqlite3
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
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

from fastapi import Body

@app.post("/updateinfo")
def update_user_info(name: str = Body(...), email: str = Body(...)):
    """Receive JSON body with name and email and update the database."""
    try:
        conn = sqlite3.connect('./chat_history.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_parameters SET (UserName, UserEmail) = ((?), (?)) "
            "WHERE Id = 1",
            (name, email)
        )
        conn.commit()
        return {"status": "ok"}
    except sqlite3.Error as db_err:
        print(f"Database creation error: {db_err}")
        return {"status": "error"}
    finally:
        if conn:
            conn.close()

@app.get("/userinfo")
def get_user_info():
    """Return stored user parameters (name and email) as JSON."""
    try:
        conn = sqlite3.connect('./chat_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT UserName, UserEmail "
            "FROM user_parameters "
            "WHERE Id = 1"
        )
        row = cursor.fetchone()
        if row:
            return {
                "UserName": row["UserName"],
                "UserEmail": row["UserEmail"]
            }
        else:
            # record not found, return empty strings
            return {"UserName": "", "UserEmail": ""}
    except sqlite3.Error as e:
        print(f"Database error fetching user info: {e}")
        return {"UserName": "", "UserEmail": ""}
    finally:
        if conn:
            conn.close()

def get_chat_history(chat_id: int):
    """Fetch previous messages for a conversation from the database"""
    try:
        conn = sqlite3.connect('./chat_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT sender, message FROM chat WHERE id = ? ORDER BY last_updated ASC",
            (chat_id,)
        )
        rows = cursor.fetchall()
        results = []
        for row in rows:
            raw_msg = row["message"]
            # try to decode JSON stored messages (normalized format)
            try:
                parsed = json.loads(raw_msg)
                role = parsed.get("role") or row["sender"]
                content = parsed.get("content") if parsed.get("content") is not None else raw_msg
            except Exception:
                role = row["sender"]
                content = raw_msg
            results.append({"role": role, "content": content})
        return results
    except sqlite3.Error as e:
        print(f"Database error fetching history: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_user_name() -> str:
    """Fetch the user's name from the database"""
    try:
        conn = sqlite3.connect('./chat_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT UserName FROM user_parameters WHERE Id = 1"
        )
        row = cursor.fetchone()
        if row and row["UserName"]:
            return row["UserName"]
        return None
    except sqlite3.Error as e:
        print(f"Database error fetching user name: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_email() -> str:
    """Fetch the user's email from the database"""
    try:
        conn = sqlite3.connect('./chat_history.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT UserEmail FROM user_parameters WHERE Id = 1"
        )
        row = cursor.fetchone()
        if row and row["UserEmail"]:
            return row["UserEmail"]
        return None
    except sqlite3.Error as e:
        print(f"Database error fetching user email: {e}")
        return None
    finally:
        if conn:
            conn.close()

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
        # recognize special prefixes for debugging and special handling
        lower_msg = message.lower().strip()
        # ensure created_id is defined for later DB writes
        created_id = chat_id

        if lower_msg.startswith("map: "):
            query = message[len("map: "):].strip()
            print(f"query: {query}")
            print("Received map request")
            try:
                response = map_service.google_maps_search(query)
                print(f"{response}")
            except Exception as e:
                response = f"Map API error: {e}"

        elif lower_msg.startswith("email: "):
            print("Received email request")     # Use MockMail with logging to the console.
            print(f"{message[7:]}")
            response = "I printed the email to the console"

        else:
            # Fetch chat history if this is a continuing conversation
            history = get_chat_history(chat_id) if chat_id > 0 else []
            user_name = get_user_name()
            user_email = get_user_email()
            response = chatbot_service.chat(message, history=history, user_name=user_name, user_email=user_email)
            created_id = chat_id
            msg_header = message[0:20]

            # if this is a new conversation, insert into conversations table
            if not chat_id or chat_id <= 0:
                try:
                    conn = sqlite3.connect('./chat_history.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO conversations(initial_prompt) VALUES (?)",
                        (msg_header,)
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
                # store messages in a normalized JSON format for future parsing
                user_msg = json.dumps({"role": "user", "content": message})
                bot_msg = json.dumps({"role": "bot", "content": response})
                cursor.execute(
                    "INSERT INTO chat(id, sender, message) VALUES (?, ?, ?)",
                    (created_id, 'user', user_msg)
                )
                cursor.execute(
                    "INSERT INTO chat(id, sender, message) VALUES (?, ?, ?)",
                    (created_id, 'bot', bot_msg)
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


# --- Scheduling support (APScheduler) ------------------------------------
def scheduled_job(chat_id: int, message: str):
    """Worker function executed by the scheduler."""
    try:
        history = get_chat_history(chat_id) if chat_id and chat_id > 0 else []
        user_name = get_user_name()
        user_email = get_user_email()
        response = chatbot_service.chat(message, history=history, user_name=user_name, user_email=user_email)

        # persist results using same normalized JSON format
        conn = sqlite3.connect('./chat_history.db')
        cursor = conn.cursor()
        user_msg = json.dumps({"role": "user", "content": message})
        bot_msg = json.dumps({"role": "bot", "content": response})
        cursor.execute(
            "INSERT INTO chat(id, sender, message) VALUES (?, ?, ?)",
            (chat_id, 'user', user_msg)
        )
        cursor.execute(
            "INSERT INTO chat(id, sender, message) VALUES (?, ?, ?)",
            (chat_id, 'bot', bot_msg)
        )
        conn.commit()
    except Exception as e:
        print(f"Scheduled job error: {e}")
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


# create and start scheduler
scheduler = BackgroundScheduler()
scheduler.start()


@app.post('/schedule')
def schedule_job(chat_id: int, message: str, run_after_seconds: int = 0):
    """Schedule a one-off job to run after `run_after_seconds` seconds."""
    run_time = datetime.utcnow() + timedelta(seconds=run_after_seconds)
    job = scheduler.add_job(scheduled_job, 'date', run_date=run_time, args=[chat_id, message])
    return {"job_id": job.id, "run_at": run_time.isoformat()}


@app.on_event("shutdown")
def shutdown_scheduler():
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass

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

        # normalize stored messages (they may be JSON or plain strings)
        processed = []
        for row in rows:
            item = dict(row)
            raw_msg = item.get("message")
            try:
                parsed = json.loads(raw_msg)
                sender = parsed.get("role") or item.get("sender")
                message = parsed.get("content") if parsed.get("content") is not None else raw_msg
            except Exception:
                sender = item.get("sender")
                message = raw_msg

            processed.append({
                "id": item.get("id"),
                "sender": sender,
                "message": message,
                "last_updated": item.get("last_updated")
            })

        results_objs = [Chat(**p) for p in processed]
        return {"chats": [r.__dict__ for r in results_objs]}

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
