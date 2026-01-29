import requests

r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "kimi-k2.5:cloud",
        "messages": [{"role": "user", "content": "Can you name few professors who are researching in Artificial Intelligence domain in UMD-College PArk?"}],
        "stream": False,
    },
)
print(r.json())
print(r.json()["message"]["content"])
# print(r.json()["message"]["content"])
