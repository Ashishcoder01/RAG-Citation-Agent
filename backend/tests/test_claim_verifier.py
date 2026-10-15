
from app.agents.claim_verifier import ClaimVerifier


EVIDENCE = [
    {
        "evidence_id": "E1",
        "source_name": "report.pdf",
        "page_number": 1,
        "text": "The report states that the participant is 50 years old.",
    }
]


class FakeProvider:
    def __init__(self, response: str):
        self.response = response
        self.calls = 0

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        return self.response


def test_supported_claim():
    provider = FakeProvider(
        '{"status":"supported","evidence_ids":["E1"],'
        '"explanation":"The passage states the participant is 50."}'
    )

    result = ClaimVerifier(provider).verify(
        "The participant is 50 years old.",
        EVIDENCE,
    )

    assert result.status == "supported"
    assert result.evidence_ids == ["E1"]


def test_unsupported_claim():
    provider = FakeProvider(
        '{"status":"unsupported","evidence_ids":["E1"],'
        '"explanation":"The passage does not support an age of 70."}'
    )

    result = ClaimVerifier(provider).verify(
        "The participant is 70 years old.",
        EVIDENCE,
    )

    assert result.status == "unsupported"


def test_invalid_json_returns_uncertain():
    provider = FakeProvider("This is not JSON")

    result = ClaimVerifier(provider).verify(
        "The participant is 50 years old.",
        EVIDENCE,
    )

    assert result.status == "uncertain"
    assert result.evidence_ids == []


def test_fabricated_evidence_id_is_removed():
    provider = FakeProvider(
        '{"status":"supported","evidence_ids":["E99"],'
        '"explanation":"Claim verified."}'
    )

    result = ClaimVerifier(provider).verify(
        "The participant is 50 years old.",
        EVIDENCE,
    )

    assert result.status == "uncertain"
    assert result.evidence_ids == []


def test_no_evidence_skips_provider():
    provider = FakeProvider(
        '{"status":"supported","evidence_ids":["E1"],'
        '"explanation":"Verified."}'
    )

    result = ClaimVerifier(provider).verify(
        "The participant is 50 years old.",
        [],
    )

    assert result.status == "uncertain"
    assert result.evidence_ids == []
    assert provider.calls == 0


def test_empty_claim_is_rejected():
    provider = FakeProvider("{}")

    try:
        ClaimVerifier(provider).verify("   ", EVIDENCE)
        assert False, "Expected empty claim to be rejected"
    except ValueError:
        pass


def test_supported_claim_without_evidence_ids_returns_uncertain():
    provider = FakeProvider(
        '{"status":"supported","evidence_ids":[],'
        '"explanation":"The claim appears correct."}'
    )

    result = ClaimVerifier(provider).verify(
        "The participant is 50 years old.",
        EVIDENCE,
    )

    assert result.status == "uncertain"
    assert result.evidence_ids == []
    assert "supporting evidence" in result.explanation.lower()
    assert provider.calls == 1
