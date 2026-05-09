import json
import requests

BASE = "http://127.0.0.1:8000"

cases = [
    {
        "name": "closing_message_turn1",
        "payload": {"messages": [{"role": "user", "content": "Thanks, this is enough"}]}
    },
    {
        "name": "normal_vague_turn1",
        "payload": {"messages": [{"role": "user", "content": "I need an assessment"}]}
    }
]

for case in cases:
    r = requests.post(f"{BASE}/chat", json=case["payload"], timeout=20)
    print(f"\n=== {case['name']} ===")
    print("status:", r.status_code)
    print(json.dumps(r.json(), indent=2))
