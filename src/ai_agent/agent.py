"""
AI Agent for Todo Chatbot
Uses OpenAI's Assistant API with MCP tools to process natural language requests
"""

import os
import asyncio
from typing import Dict, List
from tools import TOOLS, call_tool

# System prompt for the AI assistant
SYSTEM_PROMPT = """
You are a helpful todo list assistant. You must never store information or perform business logic yourself.
Always use the provided tools to interact with the todo list system.
- Only use the add_task tool to create new tasks
- Only use the list_tasks tool to retrieve tasks
- Only use the update_task tool to modify tasks
- Only use the delete_task tool to remove tasks
- Only use the mark_task_complete tool to change completion status
Never attempt to remember, store, or process information without using these tools.
Always provide clear, helpful responses to the user based on the tool results.
"""


class TodoChatAgent:
    def __init__(self):
        self.tools = TOOLS
        self.conversation_history = []
        # Initialize OpenAI client lazily
        self._client = None

    @property
    def client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                else:
                    self._client = None
            except ImportError:
                # If openai package is not available, set client to None
                self._client = None
        return self._client

    def process_message(self, user_message: str, auth_token: str = None) -> str:
        """
        Process a user message and return an AI response
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Store the auth token for use in tool calls
        self.current_auth_token = auth_token

        if self.client:
            # Use real OpenAI API
            return self._process_with_openai(user_message)
        else:
            # Fallback implementation that simulates AI behavior
            return self._simulate_ai_response(user_message)

    def _process_with_openai(self, user_message: str) -> str:
        """
        Process message using OpenAI Assistant API with timeout and error handling
        """
        import time
        
        try:
            # Create a thread for the conversation
            thread = self.client.beta.threads.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ]
            )

            # Run the assistant with tools
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=os.getenv('TODO_ASSISTANT_ID'),  # This would need to be created separately
                tools=self.tools
            )

            # Poll for completion with timeout
            start_time = time.time()
            timeout = 30  # 30 second timeout

            while run.status in ['queued', 'in_progress']:
                # Check if we've exceeded the timeout
                if time.time() - start_time > timeout:
                    return "Sorry, the AI service is taking too long to respond. Please try again later."

                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Get the messages from the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # Extract the assistant's response
            response = ""
            for msg in messages.data:
                if msg.role == "assistant":
                    response = " ".join([item.text.value for item in msg.content if item.type == "text"])
                    break

            return response or "I processed your request, but couldn't generate a specific response."

        except Exception as e:
            # Handle specific OpenAI API errors
            error_str = str(e).lower()
            
            # Check for common API errors
            if 'rate_limit' in error_str or 'quota' in error_str or 'exceeded' in error_str:
                return "Sorry, I've reached my usage quota. Please try again later or contact the administrator."
            elif 'authentication' in error_str or 'invalid_api_key' in error_str:
                return "Sorry, there's an issue with the AI service configuration. Please contact the administrator."
            elif 'connection' in error_str or 'timeout' in error_str:
                return "Sorry, I couldn't connect to the AI service. Please try again later."
            else:
                return f"Sorry, I encountered an error processing your request: {str(e)}"

    def _simulate_ai_response(self, user_message: str) -> str:
        """
        Simulate AI response for demonstration purposes without OpenAI API
        This parses the user message and calls appropriate tools
        """
        user_message_lower = user_message.lower().strip()

        # Parse the user request and call appropriate tools
        if any(word in user_message_lower for word in ["add", "create", "new task", "make"]):
            # Extract task information from the message
            # This is a simplified extraction - in reality, you'd use more sophisticated NLP
            import re

            # Look for task title (everything after "add" or "create")
            title_match = re.search(r"(?:add|create|make)\s+(.+?)(?:\s+to\s+my\s+todo|\s+tommorow|\s+tomorrow|\s+by\s+\w+|\s+due\s+\w+|$)", user_message_lower)
            title = title_match.group(1).strip() if title_match else user_message.split(maxsplit=1)[-1]

            # Check for due date in the message
            due_date_match = re.search(r"(?:tommorow|tomorrow|due\s+(\w+)|by\s+(\w+))", user_message_lower)
            due_date = due_date_match.group(1) or due_date_match.group(2) if due_date_match else None

            try:
                # Call the add_task tool with the auth token
                result = call_tool("add_task", {
                    "title": title,
                    "description": f"Added from chat: {user_message}",
                    "due_date": due_date
                }, getattr(self, 'current_auth_token', None))

                # Check if there was an error in the result
                if "error" in result or ("result" in result and "Error" in result["result"]):
                    error_details = result.get("details", result.get("result", "Unknown error"))
                    return f"Sorry, I couldn't add the task '{title}'. Error: {error_details}"
                else:
                    return f"I've added the task '{title}' to your list. Result: {result.get('result', 'Completed')}."
            except Exception as e:
                return f"Sorry, I encountered an error while trying to add the task: {str(e)}"

        elif any(word in user_message_lower for word in ["list", "show", "display", "my tasks", "all tasks"]):
            # Determine if user wants all, completed, or pending tasks
            status = "all"
            if "completed" in user_message_lower:
                status = "completed"
            elif "pending" in user_message_lower or "incomplete" in user_message_lower:
                status = "pending"

            try:
                # Call the list_tasks tool with the auth token
                result = call_tool("list_tasks", {"status": status}, getattr(self, 'current_auth_token', None))

                if "tasks" in result:
                    tasks = result["tasks"]
                    if not tasks:
                        return f"You have no {status} tasks."

                    task_list = "\n".join([f"- {task['title']}" for task in tasks[:5]])  # Show first 5 tasks
                    remaining = len(tasks) - 5 if len(tasks) > 5 else 0
                    extra_msg = f"\n...and {remaining} more tasks." if remaining > 0 else ""

                    return f"You have {len(tasks)} {status} tasks:\n{task_list}{extra_msg}"
                else:
                    return f"I tried to list your {status} tasks, but got: {result.get('result', 'an unknown error')}."
            except Exception as e:
                return f"Sorry, I encountered an error while trying to list your tasks: {str(e)}"

        elif any(word in user_message_lower for word in ["complete", "done", "finish", "mark as"]):
            # This is more complex as we need to identify which task to mark complete
            # For simulation, we'll just say we need more info
            # In a real implementation, we'd need more sophisticated parsing
            import re

            # Look for task ID or title in the message
            id_match = re.search(r"(\d+)", user_message_lower)
            if id_match:
                task_id = int(id_match.group(1))
                try:
                    result = call_tool("mark_task_complete", {"task_id": task_id, "complete": True}, getattr(self, 'current_auth_token', None))
                    return f"I've marked task {task_id} as complete. Result: {result.get('result', 'Completed')}."
                except Exception as e:
                    return f"Sorry, I encountered an error while trying to mark the task as complete: {str(e)}"
            else:
                return "I can help mark a task as complete. Please specify which task by number or title."

        elif any(word in user_message_lower for word in ["delete", "remove", "cancel"]):
            # Look for task ID in the message
            import re
            id_match = re.search(r"(\d+)", user_message_lower)
            if id_match:
                task_id = int(id_match.group(1))
                try:
                    result = call_tool("delete_task", {"task_id": task_id}, getattr(self, 'current_auth_token', None))
                    return f"I've deleted task {task_id}. Result: {result.get('result', 'Completed')}."
                except Exception as e:
                    return f"Sorry, I encountered an error while trying to delete the task: {str(e)}"
            else:
                return "I can help delete a task. Please specify which task by number or title."

        else:
            # Default response for unrecognized commands
            return f"I understand you said: '{user_message}'. I can help you manage your todo list by adding, listing, updating, or deleting tasks. Try saying something like 'Add a task to buy groceries' or 'Show my tasks'."

    def reset_conversation(self):
        """
        Reset the conversation history
        """
        self.conversation_history = []