from typing import Tuple

VAGUE_PATTERNS = {
    "break it", "fix it", "check app", "run test", "help me", 
    "break my app", "is it safe", "test code", "audit", "simulate",
    "hack this", "stress test", "kill it"
}

def validate_incident_context(message: str) -> Tuple[bool, str]:
    """
    Evaluates whether incoming text contains actionable engineering context.
    Enforces Hackathon Rule #5 by intercepting ambiguous queries.
    """
    cleaned = message.strip().lower()
    
    # 1. Preset override check (Always allowed)
    if cleaned.startswith("/chaos"):
        return True, ""
        
    # 2. Length check
    if len(cleaned) < 15:
        rejection_msg = (
            "⚠️ **Insufficient Architecture Context (Rule #5):**\n"
            "Query is too short to construct an adversarial blast radius.\n\n"
            "Please provide at least one of the following:\n"
            "- Microservice endpoint or architecture JSON\n"
            "- Database / Cache dependencies (e.g., PostgreSQL, Redis, Kafka)\n"
            "- A predefined scenario drill: /chaos scenario=black-friday"
        )
        return False, rejection_msg

    # 3. Exact vague command check
    if cleaned in VAGUE_PATTERNS:
        rejection_msg = (
            "⚠️ **Ambiguous Chaos Target (Rule #5):**\n"
            f"Command '{message.strip()}' lacks architectural boundaries.\n\n"
            "Specify target services, message queues, or rate limits so the "
            "adversarial simulator can model cascade paths accurately."
        )
        return False, rejection_msg

    return True, ""
