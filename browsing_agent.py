import os
from browser_tools import (
    navigate_to_url,
    get_current_page_text,
    list_all_links,
    click_on_link,
    extract_information,
    find_link_by_text,
)
from ollama_agent import invoke_agent

# Use OLLAMA_MODEL env var or default to a standard Ollama model
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M")
# llama3.2:latest

def create_browsing_agent():
    """Create an agent that can browse websites using Ollama HTTP API (no streaming)."""
    tools = [
        navigate_to_url,
        get_current_page_text,
        list_all_links,
        click_on_link,
        extract_information,
        find_link_by_text,
    ]

    class AgentWrapper:
        """Wrapper so main.py can call agent.invoke({"input": user_input}) and get {"output": ...}."""

        def invoke(self, inputs: dict) -> dict:
            user_input = inputs.get("input", "")
            return invoke_agent(tools, user_input)

    return AgentWrapper()
