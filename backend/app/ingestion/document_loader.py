
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pymupdf
from docx import Document


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


@dataclass
class DocumentUnit:
    source_name: str
    page_number: int | None
    section_number: int | None
    text: str


def load_document(filename: str, content: bytes) -> list[DocumentUnit]:
    """Extract text while preserving available source metadata."""

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Upload a PDF or DOCX document."
        )

    if not content:
        raise ValueError("The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("The file exceeds the 20 MB size limit.")

    units: list[DocumentUnit] = []

    try:
        if extension == ".pdf":
            with pymupdf.open(stream=content, filetype="pdf") as pdf:
                if pdf.is_encrypted:
                    raise ValueError(
                        "Password-protected PDFs are not supported."
                    )

                for page_index, page in enumerate(pdf):
                    text = page.get_text("text").strip()

                    if text:
                        units.append(
                            DocumentUnit(
                                source_name=filename,
                                page_number=page_index + 1,
                                section_number=None,
                                text=text,
                            )
                        )

        elif extension == ".docx":
            document = Document(BytesIO(content))

            for index, paragraph in enumerate(document.paragraphs, start=1):
                text = paragraph.text.strip()

                if text:
                    units.append(
                        DocumentUnit(
                            source_name=filename,
                            page_number=None,
                            section_number=index,
                            text=text,
                        )
                    )

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "Could not read this document. Check that the file is valid."
        ) from exc

    if not units:
        raise ValueError(
            "No extractable text was found in this document."
        )

    return units
