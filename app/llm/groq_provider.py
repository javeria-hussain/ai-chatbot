from groq import AsyncGroq
from app.llm.base import LLMProvider
from app.core.config import settings


class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.llm_model

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int | None = 512,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content