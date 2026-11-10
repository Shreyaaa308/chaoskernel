import json
import logging
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiChaosClient:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == "your_gemini_api_key_here":
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.client:
            raise ValueError("GEMINI_API_KEY not configured.")

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.3,
            )
        )
        raw_text = response.text.strip()
        if raw_text.startswith("`json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("`"):
            raw_text = raw_text[3:]
        if raw_text.endswith("`"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())

chaos_llm_client = GeminiChaosClient()
