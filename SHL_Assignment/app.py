from fastapi import FastAPI
from pydantic import BaseModel
import json
import re

app = FastAPI()

# Load catalog with proper encoding
with open("catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

class Message(BaseModel):
    role: str
    content: str

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatRequest(BaseModel):
    messages: list[Message]

class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation] = []
    end_of_conversation: bool = False

def get_test_type_from_keys(keys):
    """Map SHL keys to single letter test types"""
    if not keys:
        return "O"  # Other
    
    key_mapping = {
        "Ability & Aptitude": "A",
        "Knowledge & Skills": "K",
        "Personality & Behavior": "P",
        "Biodata & Situational Judgment": "B",
        "Assessment Exercises": "E",
        "Simulations": "S",
        "Competencies": "C",
        "Development & 360": "D"
    }
    
    # Return first matching key type
    for key in keys:
        if key in key_mapping:
            return key_mapping[key]
    return "O"


def find_catalog_items_by_names(text, max_items=2):
    """Try to find up to max_items catalog entries whose names appear in text (case-insensitive)."""
    found = []
    text_lower = text.lower()
    for item in catalog:
        name = item.get("name", "")
        if name and name.lower() in text_lower:
            found.append(item)
            if len(found) >= max_items:
                break
    return found

def retrieve_relevant_assessments(query, conversation_history, limit=10):
    """Retrieve relevant assessments from catalog based on query and context"""
    
    # Build full context from all messages
    full_text = query.lower() + " " + " ".join([msg.content.lower() for msg in conversation_history])
    
    scored_items = []
    
    for item in catalog:
        score = 0
        name_lower = item.get("name", "").lower()
        desc_lower = item.get("description", "").lower()
        job_levels_raw = item.get("job_levels_raw", "").lower()
        keys_str = " ".join(item.get("keys", [])).lower()
        
        # Score based on keyword matches
        keywords = [kw for kw in full_text.split() if len(kw) > 2]
        for keyword in keywords:
            if keyword in name_lower:
                score += 5
            if keyword in keys_str:
                score += 3
            if keyword in job_levels_raw:
                score += 2
            if keyword in desc_lower:
                score += 1
        
        if score > 0:
            scored_items.append((score, item))
    
    # Sort by score and return top items
    scored_items.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in scored_items[:limit]]

def has_enough_context(messages):
    """Check if we have enough context to make recommendations"""
    if not messages:
        return False
    
    full_text = " ".join([msg.content.lower() for msg in messages])
    
    # We need indication of job level or role type, and some assessment need
    has_level_or_role = any(word in full_text for word in [
        "entry-level", "entry level", "junior", "mid", "mid-level", "mid level", "senior", "executive", "director",
        "developer", "sales", "analyst", "manager", "leadership", "graduate", "contact center", "contact centre",
        "financial", "rust", "java", "python", "engineer", "intelligence","SQL", "data", "analytics", "customer service", "cx", "call center", "call centre"
    ])
    
    has_need = any(word in full_text for word in [
        "assessment", "personality", "cognitive", "knowledge", "skill", "behavior", "behaviour",
        "reasoning", "screening", "solution", "recruit", "hiring", "test", "evaluation"
    ])
    
    return has_level_or_role and has_need

def is_off_topic(message):
    """Check if message is asking about off-topic items"""
    lower_msg = message.lower()
    off_topic_keywords = [
        "salary", "compensation", "pay",
        "legal", "lawyer", "law suit",
        "hiring practices", "discrimination",
        "patent", "proprietary",
        "how much does it cost",
        "price"
    ]
    return any(keyword in lower_msg for keyword in off_topic_keywords)


def is_closing_message(message):
    """Check if user explicitly indicates the conversation is complete."""
    lower_msg = message.lower()
    closing_keywords = [
        "thanks", "thank you", "this is enough", "that's enough", "that is enough",
        "done", "all good", "that covers it", "no more"
    ]
    return any(keyword in lower_msg for keyword in closing_keywords)

def generate_agent_response(messages, has_recs, turn_number):
    """Generate an appropriate agent response"""

    latest_user_msg = messages[-1].content if messages else ""
    lower_msg = latest_user_msg.lower()

    # If user signals completion, close gracefully.
    if is_closing_message(latest_user_msg):
        return "You're welcome. Glad I could help."

    # If user explicitly asks to compare assessments, handle that first (even on turn 1)
    if any(word in lower_msg for word in ["difference", "compare", "vs", "between"]):
        matches = find_catalog_items_by_names(latest_user_msg, max_items=2)
        if len(matches) >= 2:
            a, b = matches[0], matches[1]
            # Build a grounded comparison using catalog fields
            a_keys = ", ".join(a.get("keys", [])) or "—"
            b_keys = ", ".join(b.get("keys", [])) or "—"
            a_dur = a.get("duration", "—")
            b_dur = b.get("duration", "—")
            a_lang = ", ".join(a.get("languages", [])) or "—"
            b_lang = ", ".join(b.get("languages", [])) or "—"
            reply = (
                f"Comparison of {a.get('name')} and {b.get('name')}:\n"
                f"- {a.get('name')}: Keys: {a_keys}; Duration: {a_dur}; Languages: {a_lang}; URL: {a.get('link')}\n"
                f"- {b.get('name')}: Keys: {b_keys}; Duration: {b_dur}; Languages: {b_lang}; URL: {b.get('link')}"
            )
            return reply
        else:
            return "Let me explain the key differences between these assessments for your needs. Which two assessments would you like me to compare?"

    if turn_number == 1 and not has_recs:
        # First turn - ask clarifying questions only when we do NOT have enough context
        return "Happy to help. Could you tell me more about the role, seniority level, and what specific hiring challenges you're facing?"
    
    # Check if user is asking for comparison
    if any(word in lower_msg for word in ["difference", "compare", "vs", "between"]):
        return "Let me explain the key differences between these assessments for your needs."
    
    # Check if user is confirming
    if any(word in lower_msg for word in ["perfect", "great", "confirmed", "yes", "exactly"]):
        if has_recs:
            return "Excellent. You're all set with a solid assessment stack."
        return "Great!"
    
    # Check if user is refining
    if any(word in lower_msg for word in ["actually", "also add", "plus", "additionally", "remove"]):
        return "Got it, let me update your recommendations with that refinement."
    
    # Default response  
    if has_recs:
        return "Here are the assessments that best match your hiring needs:"
    else:
        return "To find the right assessments, could you tell me a bit more about the role, experience level, and what you're assessing?"

def should_end_conversation(messages):
    """Determine if conversation should end"""
    if len(messages) < 4:
        return False
    
    latest_msg = messages[-1].content.lower()
    
    # End if user confirms or says they're satisfied
    return any(word in latest_msg for word in ["perfect", "great", "thanks", "that's all", "that covers", "confirmed"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    """Handle chat requests"""
    
    if not req.messages:
        return ChatResponse(
            reply="Hello! I'm here to help you find the right SHL assessments for your hiring needs. Tell me about the role you're trying to fill, the seniority level, and what you're looking to assess.",
            recommendations=[],
            end_of_conversation=False
        )
    
    # Get latest user message
    user_message = req.messages[-1].content
    
    # Check for off-topic requests
    if is_off_topic(user_message):
        return ChatResponse(
            reply="I can only help with SHL assessment recommendations. I'm not able to assist with that topic.",
            recommendations=[],
            end_of_conversation=False
        )
    
    # Check if we should provide recommendations
    turn_number = (len(req.messages) + 1) // 2  # Count user turns (1, 2, 3, ...)
    # Allow recommending on Turn 1 when the single user message contains sufficient context
    should_recommend = has_enough_context(req.messages)
    
    recommendations = []
    if should_recommend:
        relevant_items = retrieve_relevant_assessments(user_message, req.messages, limit=10)
        if relevant_items:
            recommendations = []
            for item in relevant_items:
                test_type = get_test_type_from_keys(item.get("keys", []))
                recommendations.append(Recommendation(
                    name=item.get("name", "Unknown"),
                    url=item.get("link", ""),
                    test_type=test_type
                ))
    
    # Generate response
    reply = generate_agent_response(req.messages, bool(recommendations), turn_number)
    
    # Determine if conversation should end
    end_conversation = (should_end_conversation(req.messages) and bool(recommendations)) or is_closing_message(user_message)
    
    return ChatResponse(
        reply=reply,
        recommendations=recommendations,
        end_of_conversation=end_conversation
    )