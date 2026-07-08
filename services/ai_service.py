import os
import json
import logging
import ssl
import urllib.request

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("AI_MODEL", "xiaomi/mimo-v2.5")
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "You are a helpful AI assistant. Answer in Persian.",
        )
        self.ssl_ctx = ssl.create_default_context()

    def chat_sync(self, messages: list[dict], temperature: float = 0.7) -> str:
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY is not set!")
            return "API key not configured."

        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        payload = json.dumps({
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            req = urllib.request.Request(self.api_url, data=payload, headers=headers, method="POST")
            logger.info(f"Calling API: model={self.model}")
            with urllib.request.urlopen(req, timeout=60, context=self.ssl_ctx) as response:
                data = json.loads(response.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                logger.info(f"API response OK: {len(content)} chars")
                return content
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"HTTP error {e.code}: {error_body[:300]}")
            if e.code == 401:
                return "Invalid API key."
            elif e.code == 429:
                return "Rate limit exceeded. Please wait."
            else:
                return f"API error {e.code}: {error_body[:200]}"
        except Exception as e:
            logger.error(f"Exception: {type(e).__name__}: {e}")
            return f"Error: {str(e)}"

    async def chat_with_history(self, user_id: int, user_message: str, history: list[dict]) -> str:
        history.append({"role": "user", "content": user_message})

        if len(history) > 20:
            history = history[-20:]

        response = self.chat_sync(history)
        history.append({"role": "assistant", "content": response})

        return response
