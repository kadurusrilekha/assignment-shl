import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test 1: Senior leadership (like C1)
print("=== TEST 1: Senior Leadership Selection ===")
messages = [
    {"role": "user", "content": "We need a solution for senior leadership."}
]
resp = requests.post(f"{BASE_URL}/chat", json={"messages": messages})
result = resp.json()
print(f"Turn 1: {result['reply'][:100]}")
print(f"Recs: {result['recommendations'] is not None}\n")

messages.append({"role": "assistant", "content": result['reply']})
messages.append({"role": "user", "content": "CXOs and directors with 15+ years. Selection against leadership benchmark."})

resp = requests.post(f"{BASE_URL}/chat", json={"messages": messages})
result = resp.json()
print(f"Turn 2: {result['reply'][:100]}")
print(f"Recs count: {len(result['recommendations']) if result['recommendations'] else 0}")
if result['recommendations']:
    for rec in result['recommendations'][:3]:
        print(f"  - {rec['name']} ({rec['test_type']})")
print()

# Test 2: Contact center screening
print("=== TEST 2: Contact Center Screening ===")
messages = [
    {"role": "user", "content": "Screening 500 entry-level contact centre agents. Inbound calls, customer service focus."}
]
resp = requests.post(f"{BASE_URL}/chat", json={"messages": messages})
result = resp.json()
print(f"Turn 1: {result['reply'][:100]}")
print(f"Recs count: {len(result['recommendations']) if result['recommendations'] else 0}\n")

# Test 3: Off-topic refusal
print("=== TEST 3: Off-topic Request ===")
messages = [
    {"role": "user", "content": "What should we pay our new developers?"}
]
resp = requests.post(f"{BASE_URL}/chat", json={"messages": messages})
result = resp.json()
print(f"Reply: {result['reply']}")
print(f"Recs: {result['recommendations'] is not None}\n")

# Test 4: Vague query
print("=== TEST 4: Vague Query ===")
messages = [
    {"role": "user", "content": "I need an assessment"}
]
resp = requests.post(f"{BASE_URL}/chat", json={"messages": messages})
result = resp.json()
print(f"Reply: {result['reply'][:100]}")
print(f"Recs: {result['recommendations'] is not None}")
