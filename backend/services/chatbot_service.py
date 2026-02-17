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


class ChatState(TypedDict):
    """State for the chat workflow"""
    message: str
    conversation_history: list
    response: str


class ChatbotService:
    """Service for handling chatbot operations with Gemini and LangGraph"""

    def __init__(self):
        """Initialize the chatbot service"""
        self.client = client
        self.model = "gemini-3-flash-preview"
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
            self.conversation_history.append({
                "user": state["message"],
                "bot": response.text
            })
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

    def get_conversation_history(self) -> list:
        """Get the conversation history"""
        return self.conversation_history


# Initialize the service
chatbot_service = ChatbotService()