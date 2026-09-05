#!/usr/bin/env python3
"""
End-to-end verification script for Resume Builder.
Simulates full UI workflow programmatically.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
venv_site = BASE_DIR / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

from resume_builder.renderer import ResumeRenderer
from resume_builder.models import DesignSettings


def main():
    print("=" * 60)
    print("Testing End-to-End Resume Builder Workflow")
    print("=" * 60)

    sample_yaml = BASE_DIR / "resume_builder" / "samples" / "sample_resume.yaml"
    with open(sample_yaml, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    renderer = ResumeRenderer()

    # Settings from user request
    company_name = "Globathon"
    role_name = "Lead Systems Architect"
    save_dir = "~/Documents/Globathon/Resumes"

    design = DesignSettings(
        theme="engineeringresumes",
        font_family="Calibri",
        page_size="a4",
        no_footer_or_top_note=True,
        phone_number_format="international",
        allow_page_break_in_entries=True,
    )

    print("\n1. Rendering resume with settings:")
    print(f"   Company: {company_name}")
    print(f"   Role: {role_name}")
    print(f"   Font: {design.font_family}")
    print(f"   Theme: {design.theme}")
    print(f"   Page Size: {design.page_size}")
    print(f"   No footer/top note: {design.no_footer_or_top_note}")
    print(f"   Phone format: {design.phone_number_format}")
    print(f"   Allow page breaks: {design.allow_page_break_in_entries}")

    res = renderer.render_resume(
        yaml_content=yaml_content,
        company_name=company_name,
        role_name=role_name,
        save_directory=save_dir,
        design=design,
    )

    print("\n2. Pipeline Execution Results:")
    print(f"   Success: {res.success}")
    print(f"   Token: {res.token}")
    print(f"   Resolved Filename: {res.resolved_filename}")
    assert res.resolved_filename == "VinayakPastey_Resume_Lead_Systems_Architect_Globathon.pdf"

    print("\n   Steps:")
    for step in res.steps:
        status_symbol = "✓" if step.status == "completed" else "✗"
        print(f"   [{status_symbol}] {step.name} ({step.duration_ms} ms) -> {step.message}")

    assert res.success is True
    assert len(res.steps) == 5

    print("\n3. Document Metrics:")
    print(f"   Page Count: {res.metrics.page_count}")
    print(f"   Total Words: {res.metrics.total_words}")
    print(f"   Words per page: {res.metrics.page_words}")
    print(f"   Character count: {res.metrics.character_count}")
    print(f"   Preview URLs: {res.preview_urls}")

    assert res.metrics.page_count >= 1
    assert res.metrics.total_words > 0
    assert len(res.preview_urls) == res.metrics.page_count

    print("\n4. Simulating User Acceptance & Save to target location:")
    save_res = renderer.save_resume(
        token=res.token,
        custom_filename=res.resolved_filename,
        save_directory=save_dir,
    )

    print(f"   Save Success: {save_res.success}")
    print(f"   Saved Path: {save_res.saved_path}")

    assert save_res.success is True
    saved_file = Path(save_res.saved_path)
    assert saved_file.exists()
    assert saved_file.stat().st_size > 0
    print(f"   Verified file exists and is {saved_file.stat().st_size // 1024} KB!")

    print("\n" + "=" * 60)
    print("ALL VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()

