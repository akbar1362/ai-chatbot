"""
AI Service - handles communication with Groq API
"""
import httpx


class AIService:
    def __init__(self):
        import os
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "You are a helpful AI assistant. Answer in Persian.",
        )

    async def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Send chat request to Groq API"""
        if not self.api_key:
            return "API key not configured."

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
                response = await client.post(self.api_url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    return "Invalid API key."
                elif response.status_code == 429:
                    return "Rate limit exceeded. Please wait."
                else:
                    return f"API error: {response.status_code}"
        except httpx.TimeoutException:
            return "Request timed out. Please try again."
        except Exception as e:
            return f"Error: {str(e)}"

    async def chat_with_history(self, user_id: int, user_message: str, history: list[dict]) -> str:
        """Chat with conversation history"""
        history.append({"role": "user", "content": user_message})

        if len(history) > 20:
            history = history[-20:]

        response = await self.chat(history)
        history.append({"role": "assistant", "content": response})

        return response
