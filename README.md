# assignment-shl

# SHL Conversational Assessment Recommender

A FastAPI-based conversational AI agent that helps recruiters and hiring managers discover the right SHL assessments through natural multi-turn dialogue.

## Features

* Clarifies vague hiring requests before recommending assessments
* Recommends 1–10 grounded SHL assessments
* Supports multi-turn refinement
* Compares assessments when requested
* Refuses off-topic hiring/legal/salary questions
* Fully stateless FastAPI API
* Deterministic keyword-based retrieval
* Uses only SHL catalog data

---

# Project Structure

```bash
SHL_Assignment/
│
├── app.py
├── catalog.json
├── requirements.txt
├── README.md
├── APPROACH.md
├── test_api.py
├── verify.py
├── GenAI_SampleConversations/
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/kadurusrilekha/assignment-shl.git
cd assignment-shl/SHL_Assignment
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Locally

```bash
uvicorn app:app --reload
```

Server starts at:

```bash
http://127.0.0.1:8000
```

---

# API Endpoints

## Health Check

### GET `/health`

Response:

```json
{
  "status": "ok"
}
```

---

## Chat Endpoint

### POST `/chat`

Request:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a Java developer who works with stakeholders"
    },
    {
      "role": "assistant",
      "content": "Sure. What is seniority level?"
    },
    {
      "role": "user",
      "content": "Mid-level, around 4 years"
    }
  ]
}
```

Response:

```json
{
  "reply": "Here are the assessments that best match your hiring needs.",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",
      "test_type": "K"
    },
    {
      "name": "Occupational Personality Questionnaire OPQ32r",
      "url": "https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32r/",
      "test_type": "P"
    }
  ],
  "end_of_conversation": false
}
```

---

# Supported Behaviors

The conversational agent supports:

* Clarification of vague queries
* Multi-turn conversation flow
* Recommendation refinement
* Assessment comparison
* Off-topic refusal
* Stateless conversation handling

---

# Testing

Run tests using:

```bash
python test_api.py
```

Additional verification scripts:

```bash
python verify.py
python test_compare.py
python test_turn1.py
```

---

# Deployment

This project can be deployed on:

* Render
* Railway
* Fly.io
* Hugging Face Spaces

## Render Start Command

```bash
uvicorn app:app --host 0.0.0.0 --port 10000
```

---

# Technical Design

* Framework: FastAPI
* Retrieval: Keyword-based scoring
* Architecture: Stateless API
* Catalog Source: SHL Product Catalog
* Recommendation Limit: 1–10 assessments
* Response Format: Strict schema compliance

---

# Compliance with Assignment Requirements

* GET `/health`
* POST `/chat`
* Stateless architecture
* Grounded recommendations only from SHL catalog
* Empty recommendations during clarification/refusal
* Multi-turn refinement support
* Assessment comparison support
* Off-topic refusal support

---


