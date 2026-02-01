# test_ollama.py
from langchain_ollama import ChatOllama

# Try with kimi-k2.5:cloud
try:
    llm = ChatOllama(model="kimi-k2.5:cloud")
    response = llm.invoke("Hello, how are you?")
    print("kimi-k2.5:cloud works!")
    print(response.content)
except Exception as e:
    print(f"kimi-k2.5:cloud error: {e}")

# Try with llama3.2:latest
try:
    llm2 = ChatOllama(model="llama3.2:latest")
    response2 = llm2.invoke("Hello, how are you?")
    print("\nllama3.2:latest works!")
    print(response2.content)
except Exception as e:
    print(f"llama3.2:latest error: {e}")