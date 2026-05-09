import json
import requests
from pathlib import Path

BASE = "http://127.0.0.1:8000"
CATALOG = Path(__file__).resolve().parent / "catalog.json"

payload = {
    "messages": [
        {"role": "user", "content": "Hiring a Java developer who works with stakeholders"},
        {"role": "assistant", "content": "Sure. What is seniority level?"},
        {"role": "user", "content": "Mid-level, around 4 years"}
    ]
}

print("Posting payload to /chat...")
r = requests.post(f"{BASE}/chat", json=payload, timeout=20)
print("Status code:", r.status_code)
try:
    result = r.json()
except Exception as e:
    print("Failed to parse JSON response:", e)
    print(r.text)
    raise

# Basic schema checks
errors = []
for field in ("reply", "recommendations", "end_of_conversation"):
    if field not in result:
        errors.append(f"Missing field: {field}")

recs = result.get("recommendations")
if recs is None:
    errors.append("recommendations is null but expected a shortlist (turn 3)")
else:
    if not isinstance(recs, list):
        errors.append("recommendations is not a list")
    if not (1 <= len(recs) <= 10):
        errors.append(f"recommendations length out of bounds: {len(recs)}")

# Check URLs against catalog
with open(CATALOG, "r", encoding="utf-8") as f:
    catalog = json.load(f)
catalog_urls = {item.get("link","") for item in catalog}

if recs:
    for i, rec in enumerate(recs, start=1):
        url = rec.get("url","")
        if not url:
            errors.append(f"rec {i} missing url")
        elif url not in catalog_urls:
            errors.append(f"rec {i} url not in catalog: {url}")

# Print results
print(json.dumps(result, indent=2)[:1000])
if errors:
    print("\nIssues found:")
    for e in errors:
        print("-", e)
else:
    print("\nAll checks passed: schema ok, recommendation count OK, URLs present in catalog.")
