import json
from pathlib import Path

import requests

BASE_URL = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "catalog.json"


def load_catalog_urls() -> set[str]:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item.get("link", "").strip() for item in data if item.get("link")}


SCENARIOS = {
    "C1": [
        "We need a solution for senior leadership.",
        "The pool consists of CXOs, director-level postions; people with more than 15 years of experience.",
        "Selection - comparing candidates against a leadership benchmark.",
        "Perfect, that's what we need.",
    ],
    "C2": [
        "I'm hiring a senior Rust engineer for high-performance networking infrastructure. What assessments should I use?",
        "Yes, go ahead. Should I also add a cognitive test for this level?",
        "That works. Thanks.",
    ],
    "C3": [
        "We're screening 500 entry-level contact centre agents. Inbound calls, customer service focus. What should we use?",
        "English.",
        "US.",
        "Is the Contact Center Call Simulation different from the Customer Service Phone Simulation?",
        "Perfect - new simulation for volume, old solution for finalists. Confirmed.",
    ],
    "C4": [
        "Hiring graduate financial analysts - final-year students, no work experience. We need numerical reasoning and a finance knowledge test.",
        "Good. Can you also add a situational judgement element - work-context decision making for graduates?",
        "That covers it. Numerical + Graduate Scenarios as first filter, domain tests for shortlisted candidates.",
    ],
    "C5": [
        "As part of our restructuring and annual talent audit, we need to re-skill our Sales organization. What solutions do you recommend?",
        "What's the difference between OPQ and OPQ MQ Sales Report?",
        "Clear. We'll use OPQ for everyone and add MQ only where we want motivators in the Sales Report; keeping the five solutions as our audit stack.",
    ],
    "C6": [
        "We're hiring plant operators for a chemical facility. Safety is absolute top priority - reliability, procedure compliance, never cutting corners. What do you recommend?",
        "What's the difference between the DSI and the Safety & Dependability 8.0?",
        "We're industrial. The 8.0 bundle is the right fit. Confirmed.",
    ],
    "C7": [
        "We're hiring bilingual healthcare admin staff in South Texas - they handle patient records and need to be assessed in Spanish. HIPAA compliance is critical. What assessments work?",
        "They're functionally bilingual - English fluent for written work. Go with the hybrid.",
        "Are we legally required under HIPAA to test all staff who touch patient records? And does this SHL test satisfy that requirement?",
        "Understood. Keep the shortlist as-is.",
    ],
    "C8": [
        "I need to quickly screen admin assistants for Excel and Word daily.",
        "In that case, I am OK with adding a simulation - we want to capture the capabilties.",
        "That's good.",
    ],
    "C9": [
        "Here's the JD for an engineer we need to fill. Can you recommend an assessment battery? Senior Full-Stack Engineer - 5+ years across Core Java, Spring, REST API design, Angular, SQL/relational databases, AWS deployment, and Docker.",
        "Backend-leaning. Day-one priorities are Core Java and Spring; SQL is constant.",
        "Senior IC. They lead design on their own services but don't manage other engineers directly.",
        "Add AWS and Docker. Drop REST - the API design signal will already come through in Spring and the live interview.",
        "On Java - they'd be working on existing services, not greenfield. Is the Advanced level the right pick?",
        "Do we really need Verify G+ on top of all the technical tests? Feels redundant.",
        "Keep Verify G+. Locking it in.",
    ],
    "C10": [
        "We run a graduate management trainee scheme. We need a full battery - cognitive, personality, and situational judgement. All recent graduates.",
        "But can you remove the OPQ32r and replace it with something shorter? Candidates complain it takes too long.",
        "Drop the OPQ. Final list: Verify G+ and Graduate Scenarios.",
    ],
}


def validate_response(result: dict, catalog_urls: set[str], scenario_id: str, turn: int) -> list[str]:
    errors: list[str] = []

    for field in ("reply", "recommendations", "end_of_conversation"):
        if field not in result:
            errors.append(f"{scenario_id} T{turn}: missing field '{field}'")

    recs = result.get("recommendations")
    if recs is not None:
        if not isinstance(recs, list):
            errors.append(f"{scenario_id} T{turn}: recommendations is not a list/null")
            return errors
        if len(recs) > 10:
            errors.append(f"{scenario_id} T{turn}: recommendations exceeds 10 ({len(recs)})")
        for idx, rec in enumerate(recs, start=1):
            url = rec.get("url", "")
            if not url:
                errors.append(f"{scenario_id} T{turn} R{idx}: empty url")
            elif url not in catalog_urls:
                errors.append(f"{scenario_id} T{turn} R{idx}: url not in catalog: {url}")

    return errors


def run_scenario(scenario_id: str, user_turns: list[str], catalog_urls: set[str]) -> tuple[int, int, list[str]]:
    messages: list[dict[str, str]] = []
    checks = 0
    failures: list[str] = []

    for turn_idx, user_text in enumerate(user_turns, start=1):
        messages.append({"role": "user", "content": user_text})
        r = requests.post(f"{BASE_URL}/chat", json={"messages": messages}, timeout=20)
        checks += 1

        if r.status_code != 200:
            failures.append(f"{scenario_id} T{turn_idx}: HTTP {r.status_code}")
            continue

        result = r.json()
        failures.extend(validate_response(result, catalog_urls, scenario_id, turn_idx))

        assistant_reply = result.get("reply", "")
        messages.append({"role": "assistant", "content": assistant_reply})

    return checks, len(failures), failures


def main() -> None:
    print("=" * 72)
    print("C1-C10 Assignment Compliance Check")
    print("=" * 72)

    try:
        health = requests.get(f"{BASE_URL}/health", timeout=10)
        if health.status_code != 200:
            print(f"Health check failed with status {health.status_code}")
            return
    except Exception as exc:
        print(f"Health check failed: {exc}")
        return

    catalog_urls = load_catalog_urls()

    total_checks = 0
    total_failures = 0
    all_failures: list[str] = []

    for scenario_id, turns in SCENARIOS.items():
        checks, failures_count, failures = run_scenario(scenario_id, turns, catalog_urls)
        total_checks += checks
        total_failures += failures_count
        all_failures.extend(failures)
        status = "PASS" if failures_count == 0 else "FAIL"
        print(f"{scenario_id}: {status} ({checks - failures_count}/{checks} turns validated)")

    print("-" * 72)
    print(f"Total turns checked: {total_checks}")
    print(f"Total issues: {total_failures}")

    if all_failures:
        print("\nIssues:")
        for item in all_failures:
            print(f"- {item}")
    else:
        print("All C1-C10 checks passed for endpoint/schema/catalog constraints.")


if __name__ == "__main__":
    main()
