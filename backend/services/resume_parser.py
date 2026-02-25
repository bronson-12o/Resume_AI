"""Resume import service - extracts text from PDF/DOCX and parses into structured profile data."""
import io

from backend.services.ai_service import ai_service
from backend.utils.templates import RESUME_IMPORT_SYSTEM_PROMPT


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract all text from a DOCX file."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    # Also extract from tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    paragraphs.append(cell.text.strip())
    return "\n".join(paragraphs)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file."""
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def parse_resume_to_profile(text: str) -> dict:
    """Use AI to parse raw resume text into structured profile data."""
    result = ai_service.generate(
        system_prompt=RESUME_IMPORT_SYSTEM_PROMPT,
        user_prompt=f"Parse the following resume into structured profile data:\n\n{text}",
        response_format="json",
    )
    return result
