import re
from dataclasses import dataclass


CITATION_PATTERN = re.compile(r"\[(E\d+)\]")
BULLET_PATTERN = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


@dataclass
class CitationValidation:
    valid: bool
    cited_ids: list[str]
    invalid_ids: list[str]
    missing_citation: bool


def validate_citations(
    answer: str,
    available_evidence_ids: set[str],
) -> CitationValidation:
    cited_ids = list(dict.fromkeys(CITATION_PATTERN.findall(answer)))

    invalid_ids = [
        evidence_id
        for evidence_id in cited_ids
        if evidence_id not in available_evidence_ids
    ]

    missing_citation = False

    for line in answer.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # Every bullet or numbered item must have a citation.
        if BULLET_PATTERN.match(line):
            if not CITATION_PATTERN.search(line):
                missing_citation = True
                break
            continue

        # Every ordinary prose sentence must have a citation.
        sentences = re.split(r"(?<=[.!?])\s+", line)

        for sentence in sentences:
            sentence = sentence.strip()

            if sentence and not CITATION_PATTERN.search(sentence):
                missing_citation = True
                break

        if missing_citation:
            break

    return CitationValidation(
        valid=(
            bool(cited_ids)
            and not invalid_ids
            and not missing_citation
        ),
        cited_ids=cited_ids,
        invalid_ids=invalid_ids,
        missing_citation=missing_citation,
    )