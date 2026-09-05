"""
Tests for the PDF analyzer module.
"""

from pathlib import Path
import pytest

from resume_builder.analyzer import analyze_pdf
from resume_builder.renderer import ResumeRenderer
from resume_builder.models import DesignSettings


@pytest.fixture(scope="module")
def sample_pdf(tmp_path_factory):
    # Render a quick sample PDF to test analyzer
    tmp_dir = tmp_path_factory.mktemp("cache")
    renderer = ResumeRenderer(cache_dir=tmp_dir)

    yaml_path = Path(__file__).resolve().parent.parent / "resume_builder" / "samples" / "sample_resume.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    res = renderer.render_resume(
        yaml_content=yaml_content,
        company_name="Acme",
        role_name="Engineer",
        design=DesignSettings(font_family="Calibri", theme="engineeringresumes", page_size="a4"),
    )
    assert res.success is True
    pdf_path = tmp_dir / res.token / "resume.pdf"
    return pdf_path


def test_analyze_pdf_valid(sample_pdf):
    metrics = analyze_pdf(sample_pdf)
    assert metrics.page_count >= 1
    assert metrics.total_words > 50
    assert len(metrics.page_words) == metrics.page_count
    assert sum(metrics.page_words) == metrics.total_words
    assert metrics.character_count > metrics.total_words


def test_analyze_pdf_nonexistent():
    with pytest.raises(FileNotFoundError):
        analyze_pdf("nonexistent_path_to_resume.pdf")

