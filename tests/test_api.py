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
    assert "Design Settings" in text
    # Column 2: YAML Config Editor & 1-line Steps
    assert "YAML Config Editor" in text
    assert "step-validate_input" in text
    assert "step-apply_design" in text
    assert "step-execute_cli" in text
    assert "chkAllowPageBreak" in text
    assert "chkAllowSectionPageBreak" in text
    # Column 3: Interactive Preview
    assert "Interactive Preview" in text


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


def test_api_sample():
    response = client.get("/api/sample")
    assert response.status_code == 200
    data = response.json()
    assert "cv:" in data["yaml"]
    assert "Vinayak Pastey" in data["yaml"]


def test_api_render_and_preview_flow(tmp_path):
    sample_yaml = Path(__file__).resolve().parent.parent / "resume_builder" / "samples" / "sample_resume.yaml"
    content = sample_yaml.read_text(encoding="utf-8")

    payload = {
        "yaml_content": content,
        "company_name": "OpenAI",
        "role_name": "Research Scientist",
        "save_directory": str(tmp_path / "MyResumes"),
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

    # Test preview image endpoint
    img_res = client.get(f"/api/preview/{token}/page/1")
    assert img_res.status_code == 200
    assert img_res.headers["content-type"] == "image/png"

    # Test PDF preview endpoint
    pdf_res = client.get(f"/api/preview/{token}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"

    # Test save endpoint
    save_payload = {
        "token": token,
        "custom_filename": data["resolved_filename"],
        "save_directory": str(tmp_path / "Saved"),
    }
    save_res = client.post("/api/save", json=save_payload)
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["success"] is True
    assert Path(save_data["saved_path"]).exists()

