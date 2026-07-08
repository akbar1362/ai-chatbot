"""
AI Service - handles communication with Groq API
"""
import httpx
from ai_bot.config.settings import Config


class AIService:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.api_url = Config.GROQ_API_URL
        self.model = Config.GROQ_MODEL
        self.system_prompt = Config.SYSTEM_PROMPT

    async def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Send chat request to Groq API"""
        if not self.api_key:
            return "❌ کلید API تنظیم نشده است. لطفاً GROQ_API_KEY را در .env وارد کنید."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    return "❌ کلید API نامعتبر است."
                elif response.status_code == 429:
                    return "⚠️ درخواست‌ها بیش از حد مجاز هستند. لطفاً کمی صبر کنید."
                else:
                    return f"❌ خطای API: {response.status_code}"
        except httpx.TimeoutException:
            return "⚠️ پاسخ AI بیش از حد طول کشید. لطفاً دوباره تلاش کنید."
        except Exception as e:
            return f"❌ خطا: {str(e)}"

    async def simple_chat(self, user_message: str) -> str:
        """Simple single message chat"""
        messages = [{"role": "user", "content": user_message}]
        return await self.chat(messages)

    async def chat_with_history(self, user_id: int, user_message: str, history: list[dict]) -> str:
        """Chat with conversation history"""
        history.append({"role": "user", "content": user_message})

        # Keep history within limit
        if len(history) > Config.MAX_HISTORY:
            history = history[-Config.MAX_HISTORY:]

        response = await self.chat(history)
        history.append({"role": "assistant", "content": response})

        return response
