import re
from app.core.session_store import has_active_session

def validate_incident_context(message: str, room_id: str | None = None) -> tuple[bool, str]:
    cleaned = message.strip()
    lower = cleaned.lower()

    if has_active_session(room_id) and len(cleaned) >= 8:
        return True, ""

    has_github = bool(re.search(r"github\.com/[^/\s]+/[^/\s]+", lower))
    has_config = ("services:" in lower or "depends_on:" in lower or ("{" in cleaned and "}" in cleaned))
    has_preset = lower.startswith("/chaos")

    if has_github or has_config or has_preset:
        return True, ""

    vague_patterns = ["break it", "fix it", "check app", "run test", "help me", "test it", "hi", "hello"]
    if any(lower == pattern for pattern in vague_patterns) or len(cleaned) < 20:
        rejection_msg = (
            "⚠️ **Insufficient Architecture Context (Rule #5):**\n"
            "Unable to compute deterministic blast radius. Please provide one of:\n"
            "- A **GitHub Repository URL** (e.g., `https://github.com/org/repo`)\n"
            "- A **`docker-compose.yml`** or service topology JSON\n"
            "- A detailed architecture failure scenario\n"
            "- Or trigger a preset drill: `/chaos scenario=black-friday`"
        )
        return False, rejection_msg

    return True, ""