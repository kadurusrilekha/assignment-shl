import json
import requests

BASE = "http://127.0.0.1:8000"

# Turn 1 - vague request with no context (should have empty recommendations)
payload = {
    "messages": [
        {"role": "user", "content": "I need an assessment"}
    ]
}

print("Turn 1 (vague, no context):")
r = requests.post(f"{BASE}/chat", json=payload)
result = r.json()
print(json.dumps(result, indent=2))

# Check that recommendations is [] not None
if result["recommendations"] == []:
    print("✓ recommendations is [] (empty array) - CORRECT")
elif result["recommendations"] is None:
    print("✗ recommendations is None - INCORRECT (should be [])")
else:
    print(f"? recommendations is {result['recommendations']}")
