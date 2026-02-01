"""
ChatOllama wrapper that forces stream=False when calling Ollama API.
Fixes "No data received from Ollama stream" when Ollama returns an empty stream.
"""
from langchain_ollama import ChatOllama
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from typing import Any


class ChatOllamaNoStream(ChatOllama):
    """
    ChatOllama that always calls Ollama with stream=False.
    Use this when you get "No data received from Ollama stream" with tools/LangGraph.
    """

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        kwargs["stream"] = False
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        kwargs["stream"] = False
        return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
