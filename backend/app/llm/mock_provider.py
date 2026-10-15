
from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic provider for development and automated tests."""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        if not system_prompt.strip():
            raise ValueError("System prompt must not be empty.")

        if not user_prompt.strip():
            raise ValueError("User prompt must not be empty.")

        return (
            "This is a mock response for development. "
            "A real LLM provider must be connected to generate "
            "an answer based on the supplied evidence."
        )
