"""LLM client using the Groq API."""
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """Generate a response given a list of chat messages."""
        pass


class GroqClient(LLMClient):
    """Groq API LLM client."""

    def __init__(self, model: str = None, api_key: str = None):
        from groq import Groq
        self.model = model or settings.groq_model
        self.client = Groq(api_key=api_key or settings.groq_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, messages: list[dict]) -> str:
        """Generate response using the Groq API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=512,
            top_p=0.9,
        )
        return response.choices[0].message.content


def create_llm_client() -> LLMClient:
    """Factory function to create the LLM client (Groq)."""
    return GroqClient()
