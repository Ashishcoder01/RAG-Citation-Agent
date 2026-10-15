
import pytest

from app.agents.answer_service import AnswerService
from app.llm.mock_provider import MockLLMProvider
from app.retrieval.chunker import TextChunk
from app.retrieval.vector_store import SearchResult


def make_search_result() -> SearchResult:
    return SearchResult(
        chunk=TextChunk(
            chunk_id="chunk1",
            source_name="sample_report.pdf",
            page_number=2,
            section_number=None,
            text="The report identifies three major findings.",
        ),
        score=0.85,
    )


class FakeProvider:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0
        self.prompts = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.calls >= len(self.responses):
            raise AssertionError("Unexpected LLM provider call.")

        self.prompts.append(user_prompt)
        response = self.responses[self.calls]
        self.calls += 1
        return response


def supported_claim_response() -> str:
    return (
        '{"status":"supported","evidence_ids":["E1"],'
        '"explanation":"The supplied passage supports the claim."}'
    )


def test_answer_includes_question_and_evidence():
    service = AnswerService(MockLLMProvider())

    result = service.answer(
        question="What are the findings?",
        search_results=[make_search_result()],
    )

    assert result.question == "What are the findings?"
    assert "mock response" in result.answer.lower()
    assert len(result.evidence) == 1
    assert result.evidence[0]["evidence_id"] == "E1"
    assert result.evidence[0]["source_name"] == "sample_report.pdf"
    assert result.evidence[0]["page_number"] == 2
    assert isinstance(result.claim_verifications, list)


def test_answer_abstains_when_no_evidence_exists():
    service = AnswerService(MockLLMProvider())

    result = service.answer(
        question="What are the findings?",
        search_results=[],
    )

    assert "could not find relevant evidence" in result.answer.lower()
    assert result.evidence == []
    assert result.claim_verifications == []


def test_empty_question_is_rejected():
    service = AnswerService(MockLLMProvider())

    with pytest.raises(ValueError, match="Question must not be empty"):
        service.answer("   ", [make_search_result()])


def test_empty_provider_response_is_rejected():
    class EmptyProvider:
        def generate(self, system_prompt: str, user_prompt: str) -> str:
            return "   "

    service = AnswerService(EmptyProvider())

    with pytest.raises(RuntimeError, match="empty answer"):
        service.answer("What are the findings?", [make_search_result()])


def test_answer_retries_when_citation_is_missing():
    provider = FakeProvider(
        [
            "The report contains three findings.",
            "The report contains three findings [E1].",
        ]
    )
    service = AnswerService(provider)

    result = service.answer(
        question="What does the report contain?",
        search_results=[make_search_result()],
    )

    assert provider.calls == 2
    assert result.citations_valid is True
    assert result.cited_evidence_ids == ["E1"]
    assert result.missing_citation is False

def test_answer_flags_invalid_citation_after_retry():
    provider = FakeProvider(
        [
            "The report contains three findings [E9].",
            "The report contains three findings [E9].",
        ]
    )
    service = AnswerService(provider)

    result = service.answer(
        question="What does the report contain?",
        search_results=[make_search_result()],
    )

    assert result.citations_valid is False
    assert result.invalid_citation_ids == ["E9"]
    assert "Citation verification failed" in result.answer
    assert result.claim_verifications == []


def test_answer_records_unsupported_claim():
    provider = FakeProvider(
        [
            "The report identifies ten findings [E1].",
            (
                '{"status":"unsupported","evidence_ids":["E1"],'
                '"explanation":"The passage does not state that there are ten findings."}'
            ),
        ]
    )
    service = AnswerService(provider, verify_claims=True)

    result = service.answer(
        question="How many findings are identified?",
        search_results=[make_search_result()],
    )

    assert result.citations_valid is True
    assert len(result.claim_verifications) == 1
    assert result.claim_verifications[0]["status"] == "unsupported"
    assert result.claim_verifications[0]["evidence_ids"] == ["E1"]



def test_claim_verification_receives_only_its_cited_evidence():
    second_result = SearchResult(
        chunk=TextChunk(
            chunk_id="chunk2",
            source_name="another_report.pdf",
            page_number=5,
            section_number=None,
            text="The second report contains different information.",
        ),
        score=0.75,
    )

    provider = FakeProvider(
        [
            "The report identifies three findings [E1].",
            (
                '{"status":"supported","evidence_ids":["E1"],'
                '"explanation":"The cited evidence supports the claim."}'
            ),
        ]
    )

    service = AnswerService(provider, verify_claims=True)

    result = service.answer(
        question="What does the report identify?",
        search_results=[make_search_result(), second_result],
    )

    assert result.citations_valid is True
    assert len(result.claim_verifications) == 1

    # The verifier prompt must contain E1 but not unrelated E2.
    verification_prompt = provider.prompts[1]
    assert "E1" in verification_prompt
    assert "E2" not in verification_prompt
    assert "another_report.pdf" not in verification_prompt


def test_uncited_claim_is_not_sent_to_claim_verifier():
    provider = FakeProvider(
        [
            "The report identifies three findings [E1].",
            (
                '{"status":"supported","evidence_ids":["E1"],'
                '"explanation":"The cited evidence supports the claim."}'
            ),
        ]
    )

    service = AnswerService(provider, verify_claims=True)

    result = service.answer(
        question="What does the report identify?",
        search_results=[make_search_result()],
    )

    assert result.citations_valid is True
    assert len(result.claim_verifications) == 1
    assert result.claim_verifications[0]["status"] == "supported"
    assert provider.calls == 2
