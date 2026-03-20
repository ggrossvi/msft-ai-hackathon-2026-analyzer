from io import BytesIO
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a text-based PDF.

    This will not do OCR on scanned PDFs. That can be added later with an OCR service.
    """
    reader = PdfReader(BytesIO(file_bytes))
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text)

    return "\n".join(pages).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file by reading its paragraphs."""
    doc = Document(BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from a plain text or markdown file."""
    return file_bytes.decode("utf-8", errors="ignore").strip()


def extract_text(file_name: str, file_bytes: bytes) -> str:
    """
    Route the file to the correct parser.

    For images and videos, this starter returns placeholder text so the rest of the
    pipeline still works end-to-end. Later you can swap these with real enrichment.
    """
    lower_name = file_name.lower()

    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    if lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)

    if lower_name.endswith((".txt", ".md")):
        return extract_text_from_txt(file_bytes)

    if lower_name.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
        return (
            f"[IMAGE PLACEHOLDER] {file_name}\n"
            "This file was uploaded successfully. Add Azure AI Vision later if you want OCR or image captions."
        )

    if lower_name.endswith((".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm")):
        return (
            f"[VIDEO PLACEHOLDER] {file_name}\n"
            "This file was uploaded successfully. Add a transcript pipeline later for searchable video content."
        )

    return (
        f"[UNSUPPORTED OR NOT YET PARSED] {file_name}\n"
        "The file is stored in Blob Storage. Add a custom parser later if needed."
    )
