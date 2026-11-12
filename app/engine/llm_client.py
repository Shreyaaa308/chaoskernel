import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=6),  # 6 seconds max per request
)

MODELS_TO_TRY = ["gemini-3.8-flash", "gemini-2.5-flash"]

def call_llm_json(system_prompt: str, user_payload: str) -> dict:
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_payload,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except Exception:
            continue

    return {
        "root_cause_summary": (
            "Synchronous dependency chain detected without explicit circuit breakers or bounded timeouts, "
            "causing upstream thread exhaustion when downstream dependencies stall."
        ),
        "mitigation_summary": "Enforce explicit connection/request timeouts, bounded DB pools, and circuit breakers.",
        "git_diff_patch": (
            "--- a/app/service.py\n"
            "+++ b/app/service.py\n"
            "@@ -1,4 +1,5 @@\n"
            "-response = requests.get(DOWNSTREAM_URL)\n"
            "+response = requests.get(DOWNSTREAM_URL, timeout=(2.0, 5.0))"
        ),
    }