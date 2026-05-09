import requests, json

BASE = "http://127.0.0.1:8000"

payload = {
    "messages": [
        {"role": "user", "content": "Compare Java 8 (New) and Core Java (Advanced Level) (New)"}
    ]
}

r = requests.post(f"{BASE}/chat", json=payload, timeout=20)
print(r.status_code)
print(json.dumps(r.json(), indent=2))
