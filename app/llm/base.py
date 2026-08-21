from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """
    Sabhi LLM providers (Groq, kal koi aur) is interface ko follow karenge.
    Chat service sirf yeh methods jaanega, provider ki details nahi.
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
        Return: model ka text response (string)
        """
        raise NotImplementedError