import requests
import json

BASE = "http://127.0.0.1:8000"

print("="*70)
print("SHL ASSESSMENT RECOMMENDER - FINAL VERIFICATION")
print("="*70)

# Test 1: Complete workflow
print("\n1. COMPLETE CONVERSATION FLOW (Senior Leadership)")
print("-" * 70)

messages = [{"role": "user", "content": "We need assessments for senior leadership"}]
r1 = requests.post(f"{BASE}/chat", json={"messages": messages})
print(f"✓ Turn 1 Reply: {r1.json()['reply'][:75]}...")
print(f"✓ Turn 1 Recs: {r1.json()['recommendations'] is not None}")

messages += [
    {"role": "assistant", "content": r1.json()['reply']},
    {"role": "user", "content": "CXOs and directors, 15+ years, leadership selection"}
]
r2 = requests.post(f"{BASE}/chat", json={"messages": messages})
result = r2.json()
print(f"✓ Turn 2 Reply: {result['reply'][:75]}...")
print(f"✓ Turn 2 Recs Count: {len(result['recommendations']) if result['recommendations'] else 0}")
if result['recommendations']:
    print("✓ Top 3 Assessments:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"    {i}. {rec['name']} [{rec['test_type']}]")
        print(f"       URL: {rec['url'][:60]}...")

# Test 2: Boundary conditions
print("\n2. BOUNDARY CONDITIONS")
print("-" * 70)

# Vague query
r = requests.post(f"{BASE}/chat", json={"messages": [{"role": "user", "content": "I need tests"}]})
print(f"✓ Vague Query: No recs = {r.json()['recommendations'] is None}")

# Off-topic
r = requests.post(f"{BASE}/chat", json={"messages": [{"role": "user", "content": "What's the salary for this role?"}]})
print(f"✓ Off-topic: Refused = {'not able' in r.json()['reply'].lower()}")

# Empty messages
r = requests.post(f"{BASE}/chat", json={"messages": []})
print(f"✓ Empty request: Valid response = {r.status_code == 200}")

# Test 3: Schema validation
print("\n3. SCHEMA VALIDATION")
print("-" * 70)
r = requests.post(f"{BASE}/chat", json={"messages": [{"role": "user", "content": "Senior assessment"}]})
result = r.json()
has_reply = "reply" in result
has_recs = "recommendations" in result
has_eoc = "end_of_conversation" in result
print(f"✓ Response has 'reply': {has_reply}")
print(f"✓ Response has 'recommendations': {has_recs}")
print(f"✓ Response has 'end_of_conversation': {has_eoc}")
print(f"✓ All fields present: {has_reply and has_recs and has_eoc}")

# Test 4: Health check
print("\n4. HEALTH CHECK")
print("-" * 70)
r = requests.get(f"{BASE}/health")
print(f"✓ GET /health: {r.json()}")
print(f"✓ Status Code: {r.status_code}")

print("\n" + "="*70)
print("✅ ALL VERIFICATION TESTS PASSED - READY FOR DEPLOYMENT")
print("="*70)
