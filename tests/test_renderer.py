"""
Tests for the ResumeRenderer and naming helpers.
"""

from pathlib import Path
import pytest

from resume_builder.renderer import ResumeRenderer, build_filename, sanitize_name, resolve_save_path
from resume_builder.models import DesignSettings


def test_sanitize_name():
    assert sanitize_name("Senior Software Engineer") == "Senior_Software_Engineer"
    assert sanitize_name("Acme / Corp - Dept") == "Acme_Corp_Dept"
    assert sanitize_name("   Spaces   ") == "Spaces"
    assert sanitize_name("") == ""


def test_build_filename_defaults():
    # Both provided
    fname = build_filename("Principal Engineer", "Google")
    assert fname == "VinayakPastey_Resume_Principal_Engineer_Google.pdf"

    # Only role
    fname = build_filename("Staff Engineer", "")
    assert fname == "VinayakPastey_Resume_Staff_Engineer.pdf"

    # Only company
    fname = build_filename("", "Netflix")
    assert fname == "VinayakPastey_Resume_Netflix.pdf"

    # Neither
    fname = build_filename("", "")
    assert fname == "VinayakPastey_Resume.pdf"

    # Custom override
    fname = build_filename("Role", "Co", "My_Custom_Resume.pdf")
    assert fname == "My_Custom_Resume.pdf"

    fname = build_filename("Role", "Co", "My_Custom_Resume")
    assert fname == "My_Custom_Resume.pdf"


def test_renderer_full_pipeline(tmp_path):
    renderer = ResumeRenderer(cache_dir=tmp_path)
    sample_yaml = Path(__file__).resolve().parent.parent / "resume_builder" / "samples" / "sample_resume.yaml"
    content = sample_yaml.read_text(encoding="utf-8")

    design = DesignSettings(
        theme="engineeringresumes",
        font_family="Calibri",
        page_size="a4",
        no_footer_or_top_note=True,
        phone_number_format="international",
        allow_page_break_in_entries=True,
    )

    res = renderer.render_resume(
        yaml_content=content,
        company_name="Globathon",
        role_name="Lead Engineer",
        design=design,
    )

    assert res.success is True
    assert res.token != ""
    assert res.resolved_filename == "VinayakPastey_Resume_Lead_Engineer_Globathon.pdf"
    assert len(res.steps) == 5
    assert all(s.status == "completed" for s in res.steps)
    assert res.metrics is not None
    assert res.metrics.page_count >= 1
    assert res.metrics.total_words > 0
    assert len(res.preview_urls) >= 1

    # Verify session directory contents
    session_dir = tmp_path / res.token
    assert (session_dir / "resume.pdf").exists()
    assert (session_dir / "page_1.png").exists()

    # Test saving to location
    save_dest_dir = tmp_path / "SavedResumes"
    save_res = renderer.save_resume(
        token=res.token,
        custom_filename=res.resolved_filename,
        save_directory=str(save_dest_dir),
    )

    assert save_res.success is True
    assert Path(save_res.saved_path).exists()
    assert Path(save_res.saved_path).name == "VinayakPastey_Resume_Lead_Engineer_Globathon.pdf"


def test_renderer_invalid_yaml(tmp_path):
    renderer = ResumeRenderer(cache_dir=tmp_path)
    bad_yaml = "this is: [invalid: yaml: not valid"

    res = renderer.render_resume(
        yaml_content=bad_yaml,
        company_name="Test",
        role_name="Test",
    )

    assert res.success is False
    assert res.error is not None
    assert res.steps[0].status == "failed"


def test_renderer_page_break_settings(tmp_path):
    from ruamel.yaml import YAML
    renderer = ResumeRenderer(cache_dir=tmp_path)
    sample_yaml = Path(__file__).resolve().parent.parent / "resume_builder" / "samples" / "sample_resume.yaml"
    content = sample_yaml.read_text(encoding="utf-8")

    design = DesignSettings(
        theme="engineeringresumes",
        font_family="Calibri",
        page_size="a4",
        allow_page_break_in_entries=False,
        allow_page_break_in_sections=False,
    )

    res = renderer.render_resume(
        yaml_content=content,
        design=design,
    )

    assert res.success is True
    # Verify input.yaml saved in session has the flags set to False in RenderCV 2.8+ schema
    session_dir = tmp_path / res.token
    y = YAML()
    parsed = y.load((session_dir / "input.yaml").read_text(encoding="utf-8"))
    assert parsed["design"]["entries"]["allow_page_break"] is False
    assert parsed["design"]["sections"]["allow_page_break"] is False


def test_renderer_default_configs_expansion(tmp_path):
    from ruamel.yaml import YAML
    renderer = ResumeRenderer(cache_dir=tmp_path)

    # Input YAML with minimal cv section and custom margin / custom bold keyword
    custom_yaml = """
cv:
  name: Vinayak Pastey
  location: Bengaluru, India
design:
  page:
    top_margin: 1.5cm
settings:
  bold_keywords:
    - Vinayak
"""

    design = DesignSettings(
        theme="engineeringresumes",
        font_family="Calibri",
        page_size="a4",
        no_footer_or_top_note=True,
        phone_number_format="international",
        allow_page_break_in_entries=False,
    )

    res = renderer.render_resume(
        yaml_content=custom_yaml,
        design=design,
    )

    assert res.success is True
    session_dir = tmp_path / res.token
    y = YAML()
    parsed = y.load((session_dir / "input.yaml").read_text(encoding="utf-8"))

    # 1. Check all design default blocks exist for RenderCV 2.8+
    assert "theme" in parsed["design"]
    assert "page" in parsed["design"]
    assert "colors" in parsed["design"]
    assert "typography" in parsed["design"]
    assert "links" in parsed["design"]
    assert "header" in parsed["design"]
    assert "section_titles" in parsed["design"]
    assert "sections" in parsed["design"]
    assert "entries" in parsed["design"]
    assert "templates" in parsed["design"]

    # User customization preserved
    assert parsed["design"]["page"]["top_margin"] == "1.5cm"
    # UI overrides applied
    assert parsed["design"]["page"]["size"] == "a4"
    assert parsed["design"]["page"]["show_footer"] is False
    assert parsed["design"]["page"]["show_top_note"] is False
    assert parsed["design"]["entries"]["allow_page_break"] is False
    assert parsed["design"]["typography"]["font_family"] == "Calibri"
    assert parsed["design"]["header"]["connections"]["phone_number_format"] == "international"

    # 2. Check settings block exists and user settings merged cleanly
    assert "settings" in parsed
    assert "rendercv_settings" not in parsed  # Migrated cleanly
    assert parsed["settings"]["bold_keywords"] == ["Vinayak"]
    assert "current_date" in parsed["settings"]


def test_renderer_with_cover_letter(tmp_path):
    renderer = ResumeRenderer(cache_dir=tmp_path)
    sample_yaml = Path(__file__).resolve().parent.parent / "resume_builder" / "samples" / "sample_resume.yaml"
    content = sample_yaml.read_text(encoding="utf-8")

    res = renderer.render_resume(
        yaml_content=content,
        company_name="Google",
        role_name="Software Engineer",
    )

    assert res.success is True
    assert res.has_cover_letter is True
    assert len(res.preview_urls) >= 1
    assert len(res.cover_letter_preview_urls) >= 1
    assert res.cover_letter_pdf_url == f"/api/preview/{res.token}/cover-letter-pdf"
    assert res.metrics is not None
    assert res.metrics.page_count >= 1
    assert res.cover_letter_metrics is not None
    assert res.cover_letter_metrics.page_count >= 1
    assert "Cover_Letter" in res.cover_letter_resolved_filename

    # 1. Test saving resume only (default behavior when only save_resume is true)
    save_res = renderer.save_resume(
        token=res.token,
        custom_filename=res.resolved_filename,
        save_directory=str(tmp_path / "saved_resumes_only"),
        save_resume=True,
        save_cover_letter=False,
    )
    assert save_res.success is True
    assert Path(save_res.saved_path).exists()
    assert save_res.saved_cover_letter_path is None

    # 2. Test saving cover letter only
    save_cl_res = renderer.save_resume(
        token=res.token,
        custom_cover_letter_filename=res.cover_letter_resolved_filename,
        cover_letter_save_directory=str(tmp_path / "saved_cl_only"),
        save_resume=False,
        save_cover_letter=True,
    )
    assert save_cl_res.success is True
    assert save_cl_res.saved_path == ""
    assert save_cl_res.saved_cover_letter_path is not None
    assert Path(save_cl_res.saved_cover_letter_path).exists()

    # 3. Test saving both resume and cover letter
    save_both_res = renderer.save_resume(
        token=res.token,
        custom_filename=res.resolved_filename,
        save_directory=str(tmp_path / "saved_both_resumes"),
        custom_cover_letter_filename=res.cover_letter_resolved_filename,
        cover_letter_save_directory=str(tmp_path / "saved_both_cls"),
        save_resume=True,
        save_cover_letter=True,
    )
    assert save_both_res.success is True
    assert Path(save_both_res.saved_path).exists()
    assert save_both_res.saved_cover_letter_path is not None
    assert Path(save_both_res.saved_cover_letter_path).exists()



