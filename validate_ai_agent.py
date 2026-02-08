"""
Quick validation script for the AI Agent components
"""
import sys
import os

# Add AI agent to path
ai_agent_path = os.path.join(os.path.dirname(__file__), 'src', 'ai_agent')
sys.path.insert(0, ai_agent_path)

try:
    # Test tools import
    from tools import TOOLS, call_tool
    print("[OK] AI Agent tools import successfully")

    # Check if all expected tools are present
    tool_names = [tool['function']['name'] for tool in TOOLS]
    expected_tools = ['add_task', 'list_tasks', 'update_task', 'delete_task', 'mark_task_complete']

    print("[OK] Available tools:")
    for tool in tool_names:
        print(f"  - {tool}")

    all_tools_present = all(tool in tool_names for tool in expected_tools)
    if all_tools_present:
        print("[OK] All expected tools are present")
    else:
        missing = [tool for tool in expected_tools if tool not in tool_names]
        print(f"[WARNING] Missing tools: {missing}")

    # Test agent import
    from agent import TodoChatAgent
    print("[OK] AI Agent class imports successfully")

    # Test server import
    from server import app
    print("[OK] AI Agent server imports successfully")

    print("\n[OK] AI Agent validation passed!")

except ImportError as e:
    print(f"[ERROR] AI Agent import failed: {e}")
except Exception as e:
    print(f"[ERROR] AI Agent validation failed: {e}")