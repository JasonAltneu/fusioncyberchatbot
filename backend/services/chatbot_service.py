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
    user_name: Optional[str]
    user_email: Optional[str]


class ChatbotService:
    """Service for handling chatbot operations with Gemini and LangGraph"""

    def __init__(self, conversationHistory = None):
        """Initialize the chatbot service"""
        self.client = client
        self.model = "gemini-3-flash-preview"
        if(conversationHistory == None):
            self.conversation_history = []
        else:
            self.conversation_history = conversationHistory
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
            # Build system context with user's name if provided
            prompt_lines = []
            user_name = state.get("user_name")
            user_email = state.get("user_email")
            if user_name:
                prompt_lines.append(f"System: You are speaking with {user_name}.")
            if user_email:
                prompt_lines.append(f"System: The user's email address is {user_email}.")

            # Build conversation context from history as a single text prompt.
            # The Gemini `generate_content` endpoint expects string content
            # (or a list of strings), not dicts with role/content, so we
            # concatenate the prior exchanges into a readable prompt.
            messages = state.get("conversation_history") or []
            # Ensure current message is treated like the latest user entry
            all_msgs = list(messages) + [{"role": "user", "content": state["message"]}]

            for m in all_msgs:
                role = (m.get("role") or "user").lower()
                label = "User" if role.startswith("user") else "Bot"
                content = m.get("content") or m.get("message") or ""
                prompt_lines.append(f"{label}: {content}")

            prompt = "\n".join(prompt_lines)

            # Get response from Gemini using a single string prompt
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            state["response"] = response.text

            # Update conversation history in a normalized format
            self.conversation_history.append({"role": "user", "content": state["message"]})
            self.conversation_history.append({"role": "bot", "content": response.text})
        except Exception as e:
            state["response"] = f"Error: {str(e)}"

        return state

    def chat(self, message: str, history: list = None, user_name: str = None, user_email: str = None) -> str:
        """
        Main chat method. Processes message through the workflow.
        
        Args:
            message: User's input message
            history: Optional list of previous messages to provide context
            user_name: Optional user's name to include in system context
            
        Returns:
            str: Bot's response
        """
        # Use provided history if available, otherwise use internal history
        if history:
            self.conversation_history = history
        
        # Create initial state
        state = ChatState(
            message=message,
            conversation_history=self.conversation_history,
            response="",
            user_name=user_name
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