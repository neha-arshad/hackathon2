"""
Test script for AI Agent
Validates that the agent can process messages and simulate responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import TodoChatAgent


def test_agent_responses():
    """Test the agent's ability to process various messages"""
    print("Testing AI Agent responses...\n")

    agent = TodoChatAgent()

    test_messages = [
        "Add a task to buy groceries tomorrow",
        "Show my tasks",
        "Show my completed tasks",
        "Show my pending tasks",
        "Mark task 1 as complete",
        "Delete task 1",
        "What can you do?",
        "Tell me about my tasks"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: User message: '{message}'")
        response = agent.process_message(message)
        print(f"AI response: '{response}'")
        print("-" * 50)


def test_conversation_flow():
    """Test a simple conversation flow"""
    print("\nTesting conversation flow...\n")

    agent = TodoChatAgent()

    conversation = [
        "Hello!",
        "Add a task to finish the report by Friday",
        "What tasks do I have?",
        "Mark the report task as done",
        "Thanks!"
    ]

    for i, message in enumerate(conversation, 1):
        print(f"Round {i}: User: '{message}'")
        response = agent.process_message(message)
        print(f"AI: '{response}'")
        print()


if __name__ == "__main__":
    test_agent_responses()
    test_conversation_flow()
    print("Agent tests completed!")