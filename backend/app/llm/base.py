
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for interchangeable LLM providers."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate a text response from the supplied prompts."""
        raise NotImplementedError
