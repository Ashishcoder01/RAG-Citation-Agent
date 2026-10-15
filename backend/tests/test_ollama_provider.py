
import pytest

from app.llm.base import LLMProvider
from app.llm.ollama_provider import OllamaProvider


def test_ollama_provider_implements_interface():
    provider = OllamaProvider()

    assert isinstance(provider, LLMProvider)


def test_ollama_generates_a_response():
    provider = OllamaProvider(timeout=120)

    response = provider.generate(
        system_prompt="Answer clearly and briefly.",
        user_prompt="What is RAG? Explain in two sentences.",
    )

    assert isinstance(response, str)
    assert len(response) > 10


def test_ollama_rejects_empty_prompts():
    provider = OllamaProvider()

    with pytest.raises(ValueError):
        provider.generate("", "A question")

    with pytest.raises(ValueError):
        provider.generate("Instructions", "   ")
