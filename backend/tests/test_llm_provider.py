
import pytest

from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider


def test_mock_provider_implements_interface():
    provider = MockLLMProvider()

    assert isinstance(provider, LLMProvider)


def test_mock_provider_returns_response():
    provider = MockLLMProvider()

    response = provider.generate(
        system_prompt="Answer using supplied evidence.",
        user_prompt="What does the report say?",
    )

    assert isinstance(response, str)
    assert "mock response" in response.lower()


def test_mock_provider_rejects_empty_prompts():
    provider = MockLLMProvider()

    with pytest.raises(ValueError):
        provider.generate("", "A question")

    with pytest.raises(ValueError):
        provider.generate("Instructions", "   ")
