"""
API integration tests using FastAPI TestClient.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from resume_builder.app import app

client = TestClient(app)


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Resume Builder" in response.text
    assert "RenderCV CLI" in response.text
    assert "Calibri" in response.text


def test_index_three_column_layout():
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    # Check 3 columns grid setup
    assert "grid grid-cols-1 lg:grid-cols-12" in text
    assert "lg:col-span-3" in text
    assert "lg:col-span-4" in text
    assert "lg:col-span-5" in text
    # Column 1: Application Target & Design Settings
    assert "Application Target" in text
    assert "Resume Target" in text
    assert "Cover Letter Target" in text
    assert "coverLetterSaveDirectory" in text
    assert "lblCoverLetterFilenamePreview" in text
    assert "Design Settings" in text
    # Column 2: YAML Config Editor & 1-line Steps
    assert "YAML Config Editor" in text
    assert "step-validate_input" in text
    assert "step-apply_design" in text
    assert "step-execute_cli" in text
    assert "chkAllowPageBreak" in text
    assert "chkAllowSectionPageBreak" in text
    # Column 3: Interactive Preview & Document Switcher
    assert "Interactive Preview" in text
    assert "docTabSelector" in text
    assert "tabCoverLetter" in text
    assert "btnSaveBoth" in text


def test_fullscreen_preview_modal():
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    # Full Screen Preview controls & modal verification
    assert "btnFullscreenPreview" in text
    assert "fullscreenPreviewModal" in text
    assert "btnFullscreenDocToggle" in text
    assert "fullscreenDocToggleLabel" in text
    assert "fullscreenPagesContainer" in text
    assert "btnCloseFullscreenModal" in text
    assert "fullscreenPreviewViewport" in text



def test_api_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["default_theme"] == "engineeringresumes"
    assert data["default_font"] == "Calibri"
    assert data["default_page_size"] == "a4"
    assert data["default_phone_format"] == "international"
    assert data["default_allow_page_break_in_entries"] is True
    assert data["default_allow_page_break_in_sections"] is True
    assert data["default_save_dir"] == "~/Documents/Globathon/Resumes"
    assert data["default_cover_letter_save_dir"] == "~/Documents/Globathon/CoverLetters"


def test_api_sample():
    response = client.get("/api/sample")
    assert response.status_code == 200
    data = response.json()
    assert "cv:" in data["yaml"]
    assert "Vinayak Pastey" in data["yaml"]
    assert "cover_letter:" in data["yaml"]


def test_api_render_and_preview_flow(tmp_path):
    sample_yaml = Path(__file__).resolve().parent.parent / "resume_builder" / "samples" / "sample_resume.yaml"
    content = sample_yaml.read_text(encoding="utf-8")

    payload = {
        "yaml_content": content,
        "company_name": "OpenAI",
        "role_name": "Research Scientist",
        "save_directory": str(tmp_path / "MyResumes"),
        "cover_letter_save_directory": str(tmp_path / "MyCoverLetters"),
        "design": {
            "theme": "engineeringresumes",
            "font_family": "Calibri",
            "page_size": "a4",
            "no_footer_or_top_note": True,
            "phone_number_format": "international",
            "allow_page_break_in_entries": True,
        },
    }

    render_res = client.post("/api/render", json=payload)
    assert render_res.status_code == 200
    data = render_res.json()
    assert data["success"] is True
    token = data["token"]
    assert data["resolved_filename"] == "VinayakPastey_Resume_Research_Scientist_OpenAI.pdf"
    assert data["metrics"]["page_count"] >= 1
    assert data["metrics"]["total_words"] > 0
    assert len(data["preview_urls"]) >= 1

    # Cover letter assertions
    assert data["has_cover_letter"] is True
    assert len(data["cover_letter_preview_urls"]) >= 1
    assert data["cover_letter_pdf_url"] == f"/api/preview/{token}/cover-letter-pdf"
    assert data["cover_letter_metrics"] is not None
    assert data["cover_letter_metrics"]["page_count"] >= 1
    assert data["cover_letter_metrics"]["total_words"] > 0

    # Test preview image endpoint
    img_res = client.get(f"/api/preview/{token}/page/1")
    assert img_res.status_code == 200
    assert img_res.headers["content-type"] == "image/png"

    # Test cover letter preview image endpoint
    cl_img_res = client.get(f"/api/preview/{token}/cover-letter-page/1")
    assert cl_img_res.status_code == 200
    assert cl_img_res.headers["content-type"] == "image/png"

    # Test PDF preview endpoint
    pdf_res = client.get(f"/api/preview/{token}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"

    # Test cover letter PDF preview endpoint
    cl_pdf_res = client.get(f"/api/preview/{token}/cover-letter-pdf")
    assert cl_pdf_res.status_code == 200
    assert cl_pdf_res.headers["content-type"] == "application/pdf"

    # 1. Test saving ONLY Resume
    save_resume_payload = {
        "token": token,
        "custom_filename": data["resolved_filename"],
        "save_directory": str(tmp_path / "Saved_Resume_Only"),
        "save_resume": True,
        "save_cover_letter": False,
    }
    res1 = client.post("/api/save", json=save_resume_payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is True
    assert Path(data1["saved_path"]).exists()
    assert data1["saved_cover_letter_path"] is None

    # 2. Test saving ONLY Cover Letter
    save_cl_payload = {
        "token": token,
        "custom_cover_letter_filename": data["cover_letter_resolved_filename"],
        "cover_letter_save_directory": str(tmp_path / "Saved_CL_Only"),
        "save_resume": False,
        "save_cover_letter": True,
    }
    res2 = client.post("/api/save", json=save_cl_payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["saved_path"] == ""
    assert data2["saved_cover_letter_path"] is not None
    assert Path(data2["saved_cover_letter_path"]).exists()

    # 3. Test saving BOTH
    save_both_payload = {
        "token": token,
        "custom_filename": data["resolved_filename"],
        "save_directory": str(tmp_path / "Saved_Both_Resumes"),
        "custom_cover_letter_filename": data["cover_letter_resolved_filename"],
        "cover_letter_save_directory": str(tmp_path / "Saved_Both_CLs"),
        "save_resume": True,
        "save_cover_letter": True,
    }
    res3 = client.post("/api/save", json=save_both_payload)
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["success"] is True
    assert Path(data3["saved_path"]).exists()
    assert data3["saved_cover_letter_path"] is not None
    assert Path(data3["saved_cover_letter_path"]).exists()

