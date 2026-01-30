import requests

r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "kimi-k2.5:cloud",
        "messages": [{"role": "user", "content": "Can you find emails of professors from the page: https://www.cs.umd.edu/people/faculty"}],
        "stream": False,
    },
)
# print(r.json())
print(r.json()["message"]["content"])
# print(r.json()["message"]["content"])
