# SHL Conversational Assessment Recommender - Approach Document

## 1. Design Choices

The product goal is to move a user from vague hiring intent to a grounded shortlist from the SHL catalog through dialogue. I implemented a stateless FastAPI service with two endpoints:

- GET /health for service availability checks
- POST /chat for multi-turn conversational recommendations

The agent behavior follows four required modes:

- Clarify: ask for role, seniority, and hiring objective when context is incomplete
- Recommend: return 1 to 10 catalog-grounded assessments
- Refine: update recommendations when constraints change
- Compare: answer differences between assessments in conversation

I chose deterministic logic over external LLM inference to maximize reliability, speed, and repeatability for automated evaluation.

## 2. Retrieval Setup

Catalog source is catalog.json (377 SHL items). Recommendations are produced only from this file.

Retrieval pipeline:

1. Build a query context from the latest user turn plus prior conversation text.
2. Score each catalog item with weighted keyword matches:

   score = name x 5 + keys x 3 + job levels x 2 + description x 1

3. Sort by score descending and return top 10.

This setup prioritizes exact role and assessment intent terms while still capturing broader context in descriptions.

## 3. Prompt and Conversation Design

No external prompt template is used because the final version is heuristic. Conversation policy is implemented directly in application logic:

- Turn 1 asks clarification when context is insufficient; if context is already sufficient, it can recommend immediately.
- Recommendations are generated when both context dimensions are present:
  - role or seniority signal
  - assessment intent signal
- Off-topic requests (salary, legal, patent, pricing) are refused.
- Responses always follow the required schema:
  - reply
  - recommendations (always a list; empty [] while clarifying/refusing, 1-10 items when committing)
  - end_of_conversation (boolean)

This keeps outputs stable and testable across repeated runs.

## 4. Evaluation Approach

I evaluated in three layers:

1. Endpoint checks
- GET /health returns status ok
- POST /chat returns valid JSON schema

2. Scenario checks
- test_api.py validates clarification, recommendation, refusal, and vague-query handling

3. C1 to C10 batch checks
- run_c1_c10_checks.py simulates all sample conversation turns
- validates recommendations <= 10
- validates every recommendation URL exists in catalog.json

Observed outcome in current run:

- 38/38 turns passed
- 0 schema or catalog-grounding issues

## 5. What Did Not Work and Improvements

Initial approach tried external LLM integration. It failed practical constraints in this environment:

- dependency/import issues during setup
- latency/timeouts affecting reliability
- less deterministic behavior for strict catalog-grounded outputs

After pivoting to deterministic retrieval:

- stability improved (no runtime LLM dependency)
- latency improved (fast local scoring)
- grounding improved (recommendations constrained to catalog file only)

Improvement was measured by repeated endpoint tests, scenario tests, and full C1 to C10 validation.

## 6. AI Tooling Usage

AI coding assistance was used for:

- implementation acceleration for FastAPI endpoint scaffolding
- iterative debugging and refactoring
- test script generation and validation workflow setup
- document drafting and tightening for submission

Final behavior and constraints were enforced in code and validated with deterministic tests.

## 7. Trade-offs

Advantages of final design:

- deterministic and reproducible
- no hallucinated assessments
- simple deployment and low runtime complexity

Limitations:

- keyword matching is less semantically rich than embedding or LLM retrieval
- deeper domain paraphrases may require manual keyword expansion

Given assignment requirements, this trade-off favors reliability and scoring consistency.
