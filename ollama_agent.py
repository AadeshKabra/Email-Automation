"""
Custom agent that calls Ollama HTTP API with stream=false only.
Bypasses langchain_ollama and LangGraph to avoid "No data received from Ollama stream".
"""
import json
import os
from typing import Any

import requests

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_AGENT_ITERATIONS = 25


def _get_tool_name(tool: Any, index: int) -> str:
    """Get tool name safely for LangChain StructuredTool and others."""
    try:
        return getattr(tool, "name", None) or ""
    except Exception:
        pass
    try:
        return getattr(tool, "func", tool).__name__
    except Exception:
        return f"tool_{index}"


def _tool_to_ollama_format(tool: Any, index: int = 0) -> dict:
    """Convert a LangChain tool to Ollama API tools format."""
    name = _get_tool_name(tool, index) or "unknown"
    desc = getattr(tool, "description", "") or ""
    params: dict = {"type": "object", "properties": {}, "required": []}
    try:
        schema = tool.get_input_schema()
        if hasattr(schema, "model_json_schema"):
            raw = schema.model_json_schema()
            params = raw.get("properties", params)
            if "required" in raw:
                params = {"type": "object", "properties": params, "required": raw["required"]}
            else:
                params = {"type": "object", "properties": params, "required": list(params.keys()) if params else []}
    except Exception:
        pass
    if isinstance(params, dict) and "type" not in params:
        params = {"type": "object", "properties": params, "required": list(params.keys()) if params else []}
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": params}}


def _ollama_chat(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """Call Ollama /api/chat with stream=false. Returns the full JSON response."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    body = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    if tools:
        body["tools"] = tools
    resp = requests.post(url, json=body, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _run_tool_by_name(tools_by_name: dict[str, Any], name: str, arguments: dict) -> str:
    """Invoke a LangChain tool by name with the given arguments. Returns result as string."""
    tool = tools_by_name.get(name)
    if not tool:
        return f"Error: unknown tool '{name}'"
    try:
        result = tool.invoke(arguments)
        return str(result) if result is not None else ""
    except Exception as e:
        return f"Error: {e}"


def run_agent(tools: list[Any], user_input: str) -> str:
    """
    Run a simple ReAct-style loop: call Ollama with stream=false, execute tool_calls, repeat.
    Returns the final text answer.
    """
    ollama_tools = [_tool_to_ollama_format(t, i) for i, t in enumerate(tools)]
    tools_by_name = {_get_tool_name(t, i): t for i, t in enumerate(tools)}
    messages: list[dict] = [{"role": "user", "content": user_input}]

    for _ in range(MAX_AGENT_ITERATIONS):
        response = _ollama_chat(messages, tools=ollama_tools)
        msg = response.get("message") or {}
        content = (msg.get("content") or "").strip()
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            return content or "No response from model."

        # Append assistant message with tool_calls (Ollama format)
        assistant_msg = {"role": "assistant", "content": content or ""}
        if tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "type": "function",
                    "function": {
                        "index": i,
                        "name": tc.get("function", {}).get("name", ""),
                        "arguments": tc.get("function", {}).get("arguments", {}),
                    },
                }
                for i, tc in enumerate(tool_calls)
            ]
        messages.append(assistant_msg)

        # Run each tool and append tool results
        for tc in tool_calls:
            fn = tc.get("function") if isinstance(tc, dict) else {}
            if not fn and isinstance(tc, dict):
                fn = tc
            name = (fn or {}).get("name", "")
            args_raw = (fn or {}).get("arguments")
            if isinstance(args_raw, str):
                try:
                    args = json.loads(args_raw) if args_raw.strip() else {}
                except json.JSONDecodeError:
                    args = {}
            else:
                args = args_raw if isinstance(args_raw, dict) else {}
            result = _run_tool_by_name(tools_by_name, name, args)
            messages.append({"role": "tool", "tool_name": name, "content": result})

    return "Max iterations reached without final answer."


def invoke_agent(tools: list[Any], user_input: str) -> dict:
    """Same interface as LangGraph agent: input with 'input' key, output with 'output' key."""
    output = run_agent(tools, user_input)
    return {"output": output}


def ollama_simple_chat(prompt: str) -> str:
    """Call Ollama /api/chat with stream=false for a single user message. Returns assistant content."""
    messages = [{"role": "user", "content": prompt}]
    response = _ollama_chat(messages, tools=None)
    msg = response.get("message") or {}
    return (msg.get("content") or "").strip()
