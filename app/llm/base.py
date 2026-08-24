from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """
    All LLM providers (Groq, or anyone else tomorrow) will follow this interface. The chat service will only know these methods, not the provider details.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = 512,
    ) -> str:
        """
        messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
        Return: model's response (string)
        """
        raise NotImplementedError
