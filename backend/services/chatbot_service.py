"""
Chatbot Service Module

This module handles the chatbot logic using Google Gemini API and LangGraph
for managing conversation state and workflow.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from google import genai
from langgraph.graph import StateGraph # type: ignore
from typing_extensions import TypedDict

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=GEMINI_API_KEY)

# Simple SQLite helper used for storing conversation history if desired
import sqlite3

DB_PATH = os.environ.get('CHAT_DB_PATH', '../chat_history.db')

def get_db_connection():
    """Return a connection to the SQLite database, creating schema if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create tables that don't already exist."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user TEXT NOT NULL,
            bot TEXT NOT NULL,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


class ChatState(TypedDict):
    """State for the chat workflow"""
    message: str
    conversation_history: list
    response: str


class ChatbotService:
    """Service for handling chatbot operations with Gemini and LangGraph"""

    def __init__(self, conversationHistory: Optional[list] = None, session_id: Optional[str] = None):
        """Initialize the chatbot service.

        Args:
            conversationHistory: optional pre‑loaded list of turns.
            session_id: unique identifier for this chat session; if provided the
                history will be read from and written to the SQLite database.
        """
        self.client = client
        self.model = "gemini-3-flash-preview"
        self.session_id = session_id

        if session_id and conversationHistory is None:
            # fetch existing history from db
            self.conversation_history = self._load_history_from_db()
            print(f"{self.conversation_history}")
        elif conversationHistory is not None:
            self.conversation_history = conversationHistory
        else:
            self.conversation_history = []

        self.graph = self._build_workflow()

    def _build_workflow(self):
        """
        Build the LangGraph workflow for the chatbot.
        This defines the conversation flow.
        """
        workflow = StateGraph(ChatState)

        # Add nodes
        workflow.add_node("process_message", self._process_message_node)
        workflow.add_node("generate_response", self._generate_response_node)

        # Define edges
        workflow.set_entry_point("process_message")
        workflow.add_edge("process_message", "generate_response")
        workflow.set_finish_point("generate_response")

        return workflow.compile()

    def _process_message_node(self, state: ChatState) -> ChatState:
        """
        Process incoming message node.
        Placeholder for message validation/preprocessing.
        """
        # TODO: Add message preprocessing, validation, etc.
        return state

    def _generate_response_node(self, state: ChatState) -> ChatState:
        """
        Generate response using Gemini API.
        """
        try:
            # Get response from Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=state["message"]
            )
            state["response"] = response.text
            
            # Update conversation history
            turn = {"user": state["message"], "bot": response.text}
            self.conversation_history.append(turn)
            if self.session_id:
                self._append_turn_to_db(turn)
        except Exception as e:
            state["response"] = f"Error: {str(e)}"

        return state

    def chat(self, message: str) -> str:
        """
        Main chat method. Processes message through the workflow.
        
        Args:
            message: User's input message
            
        Returns:
            str: Bot's response
        """
        # Create initial state
        state = ChatState(
            message=message,
            conversation_history=self.conversation_history,
            response=""
        )

        # Run through workflow
        result = self.graph.invoke(state)
        return result["response"]

    def reset_conversation(self) -> None:
        """Reset conversation history"""
        self.conversation_history = []
        if self.session_id:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM history WHERE session_id=?", (self.session_id,))
            conn.commit()

    def get_conversation_history(self) -> list:
        """Get the conversation history"""
        return self.conversation_history

    # database helper methods
    def _load_history_from_db(self) -> list:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user, bot FROM history WHERE session_id=? ORDER BY ts",
            (self.session_id,)
        )
        rows = cur.fetchall()
        return [{"user": r["user"], "bot": r["bot"]} for r in rows]

    def _append_turn_to_db(self, turn: dict) -> None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO history(session_id, user, bot) VALUES (?,?,?)",
            (self.session_id, turn["user"], turn["bot"]),
        )
        conn.commit()


# Initialize the service
chatbot_service = ChatbotService()