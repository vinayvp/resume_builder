"""
PDF analysis module for resume_builder.
Extracts page count, word count, character count, and per-page metrics.
"""

from pathlib import Path
import re
from typing import Union
from pypdf import PdfReader

from .models import AnalysisResult


def analyze_pdf(pdf_path: Union[str, Path]) -> AnalysisResult:
    """
    Analyzes a rendered PDF file and returns page count and word count statistics.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    reader = PdfReader(str(path))
    num_pages = len(reader.pages)

    page_words = []
    total_words = 0
    total_chars = 0

    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # Find words (alphanumeric sequences, handling hyphens and apostrophes sensibly)
        words = re.findall(r"\b[\w'-]+\b", text)
        w_count = len(words)
        page_words.append(w_count)
        total_words += w_count
        total_chars += len(text)

    return AnalysisResult(
        page_count=num_pages,
        total_words=total_words,
        page_words=page_words,
        character_count=total_chars,
    )

