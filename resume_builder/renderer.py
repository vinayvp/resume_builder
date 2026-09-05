"""
Renderer module for resume_builder.
Orchestrates YAML preprocessing, RenderCV CLI execution, step tracking,
PDF analytics, preview caching, and final file commitment.
"""

import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ruamel.yaml import YAML

from .analyzer import analyze_pdf
from .config import (
    CACHE_DIR,
    DEFAULT_FILENAME_PATTERN,
    DEFAULT_SAVE_DIR,
)
from .models import DesignSettings, RenderResponse, SaveResponse, StepInfo


def sanitize_name(name: str) -> str:
    """
    Sanitizes role and company names for safe, clean filenames.
    Replaces whitespace, slashes, and non-alphanumeric chars with single underscores.
    """
    if not name:
        return ""
    # Replace any sequence of non-alphanumeric characters (spaces, slashes, punctuation) with '_'
    name = re.sub(r"[^\w]+", "_", name.strip())
    # Collapse multiple underscores and trim ends
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def get_rendercv_command(input_yaml_path: str, output_dir_name: str) -> List[str]:
    """
    Locates the correct Python/RenderCV binary and constructs the CLI invocation.
    """
    base_dir = Path(__file__).resolve().parent.parent
    venv_python = base_dir / ".venv" / "bin" / "python"
    venv_rcv = base_dir / ".venv" / "bin" / "rendercv"

    if venv_python.exists():
        py_bin = str(venv_python)
        cmd = [
            py_bin,
            "-m",
            "rendercv",
            "render",
            str(input_yaml_path),
            "--output-folder-name",
            output_dir_name,
            "--dont-generate-markdown",
            "--dont-generate-html",
        ]
    elif venv_rcv.exists():
        cmd = [
            str(venv_rcv),
            "render",
            str(input_yaml_path),
            "--output-folder-name",
            output_dir_name,
            "--dont-generate-markdown",
            "--dont-generate-html",
        ]
    elif shutil.which("rendercv"):
        cmd = [
            shutil.which("rendercv"),
            "render",
            str(input_yaml_path),
            "--output-folder-name",
            output_dir_name,
            "--dont-generate-markdown",
            "--dont-generate-html",
        ]
    else:
        cmd = [
            sys.executable,
            "-m",
            "rendercv",
            "render",
            str(input_yaml_path),
            "--output-folder-name",
            output_dir_name,
            "--dont-generate-markdown",
            "--dont-generate-html",
        ]
    return cmd


def build_filename(role: str, company: str, custom_name: Optional[str] = None) -> str:
    """
    Constructs the final resume filename.
    Defaults to: VinayakPastey_Resume_<role-name>_<company-name>.pdf
    """
    if custom_name and custom_name.strip():
        name = custom_name.strip()
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        return name

    clean_role = sanitize_name(role)
    clean_company = sanitize_name(company)

    if clean_role and clean_company:
        return f"VinayakPastey_Resume_{clean_role}_{clean_company}.pdf"
    elif clean_role:
        return f"VinayakPastey_Resume_{clean_role}.pdf"
    elif clean_company:
        return f"VinayakPastey_Resume_{clean_company}.pdf"
    else:
        return "VinayakPastey_Resume.pdf"


def resolve_save_path(save_dir: str, filename: str) -> Path:
    """
    Expands home path (e.g. ~/Documents/Globathon/Resumes) and joins filename.
    """
    expanded = os.path.expanduser(save_dir)
    return Path(expanded) / filename


class ResumeRenderer:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    def render_resume(
        self,
        yaml_content: str,
        company_name: str = "",
        role_name: str = "",
        custom_filename: Optional[str] = None,
        save_directory: str = DEFAULT_SAVE_DIR,
        design: Optional[DesignSettings] = None,
    ) -> RenderResponse:
        """
        Executes the 5-step rendering pipeline and returns the full response with preview tokens.
        """
        if design is None:
            design = DesignSettings()

        token = str(uuid.uuid4())
        session_dir = self.cache_dir / token
        session_dir.mkdir(parents=True, exist_ok=True)

        steps: List[StepInfo] = [
            StepInfo(
                id="validate_input",
                name="Validate YAML Specification",
                description="Parse syntax and check resume data structure",
            ),
            StepInfo(
                id="apply_design",
                name="Apply Design & Typography",
                description=f"Theme: {design.theme}, Font: {design.font_family}, Size: {design.page_size}",
            ),
            StepInfo(
                id="execute_cli",
                name="Execute RenderCV CLI Engine",
                description="Run rendercv render CLI with Typst generation",
            ),
            StepInfo(
                id="analyze_metrics",
                name="Analyze Document Metrics",
                description="Extract exact page count and word distribution",
            ),
            StepInfo(
                id="prepare_preview",
                name="Generate Visual Preview",
                description="Prepare high-resolution page previews for review",
            ),
        ]

        resolved_filename = build_filename(role_name, company_name, custom_filename)
        response = RenderResponse(
            token=token,
            success=False,
            steps=steps,
            resolved_filename=resolved_filename,
            save_directory=save_directory,
        )

        cli_logs = []

        try:
            # -------------------------------------------------------------
            # STEP 1: Parse YAML & Validate
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[0].status = "running"
            
            try:
                data = self.yaml.load(yaml_content)
            except Exception as e:
                steps[0].status = "failed"
                steps[0].message = f"YAML Syntax Error: {str(e)}"
                response.error = f"Invalid YAML content: {str(e)}"
                return response

            if not isinstance(data, dict) or "cv" not in data:
                steps[0].status = "failed"
                steps[0].message = "Missing root 'cv' section in YAML."
                response.error = "Invalid RenderCV YAML: Missing top-level 'cv' key."
                return response

            steps[0].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[0].status = "completed"
            steps[0].message = f"Successfully parsed resume for '{data['cv'].get('name', 'Applicant')}'"

            # -------------------------------------------------------------
            # STEP 2: Apply Design & Typography Settings
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[1].status = "running"

            if "design" not in data or not isinstance(data["design"], dict):
                data["design"] = {}

            # Theme
            data["design"]["theme"] = design.theme

            # Page settings
            if "page" not in data["design"] or not isinstance(data["design"]["page"], dict):
                data["design"]["page"] = {}
            data["design"]["page"]["size"] = design.page_size

            # Footer / Top note handling
            if design.no_footer_or_top_note:
                data["design"]["page"]["show_page_numbering"] = False
                data["design"]["page"]["show_last_updated_date"] = False
            else:
                if design.show_page_numbering is not None:
                    data["design"]["page"]["show_page_numbering"] = design.show_page_numbering
                if design.show_last_updated_date is not None:
                    data["design"]["page"]["show_last_updated_date"] = design.show_last_updated_date

            # Font settings (apply to all font slots)
            if "text" not in data["design"] or not isinstance(data["design"]["text"], dict):
                data["design"]["text"] = {}
            data["design"]["text"]["font_family"] = design.font_family

            if "header" not in data["design"] or not isinstance(data["design"]["header"], dict):
                data["design"]["header"] = {}
            data["design"]["header"]["name_font_family"] = design.font_family
            data["design"]["header"]["connections_font_family"] = design.font_family

            if "section_titles" not in data["design"] or not isinstance(data["design"]["section_titles"], dict):
                data["design"]["section_titles"] = {}
            data["design"]["section_titles"]["font_family"] = design.font_family

            # Entry page breaks
            if "entries" not in data["design"] or not isinstance(data["design"]["entries"], dict):
                data["design"]["entries"] = {}
            data["design"]["entries"]["allow_page_break_in_entries"] = design.allow_page_break_in_entries
            data["design"]["entries"]["allow_page_break_in_sections"] = True

            # Locale / Phone format
            if "locale" not in data or not isinstance(data["locale"], dict):
                data["locale"] = {}
            data["locale"]["phone_number_format"] = design.phone_number_format

            # Save modified YAML to session directory
            input_yaml_path = session_dir / "input.yaml"
            with open(input_yaml_path, "w", encoding="utf-8") as f:
                self.yaml.dump(data, f)

            steps[1].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[1].status = "completed"
            steps[1].message = f"Configured {design.theme} theme with {design.font_family} font and {design.page_size.upper()} layout"

            # -------------------------------------------------------------
            # STEP 3: Execute RenderCV CLI
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[2].status = "running"

            output_dir_name = "output"
            cli_cmd = get_rendercv_command(str(input_yaml_path), output_dir_name)

            process = subprocess.run(
                cli_cmd,
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )

            raw_logs = f"Command: {' '.join(cli_cmd)}\n\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
            cli_logs.append(raw_logs)

            if process.returncode != 0:
                steps[2].status = "failed"
                steps[2].message = f"RenderCV CLI failed (Exit code {process.returncode})"
                response.error = f"RenderCV execution error:\n{process.stderr or process.stdout}"
                response.cli_logs = "\n\n".join(cli_logs)
                return response

            # Verify output files
            out_folder = session_dir / output_dir_name
            pdf_files = list(out_folder.glob("*.pdf"))
            if not pdf_files:
                steps[2].status = "failed"
                steps[2].message = "RenderCV completed but no PDF was generated."
                response.error = "RenderCV finished but no PDF output was found."
                response.cli_logs = "\n\n".join(cli_logs)
                return response

            pdf_file = pdf_files[0]
            # Rename/copy to session root standard name for quick access
            session_pdf = session_dir / "resume.pdf"
            shutil.copy2(pdf_file, session_pdf)

            steps[2].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[2].status = "completed"
            steps[2].message = f"CLI rendered Typst to PDF ({pdf_file.stat().st_size // 1024} KB)"

            # -------------------------------------------------------------
            # STEP 4: Analyze Metrics
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[3].status = "running"

            metrics = analyze_pdf(session_pdf)
            response.metrics = metrics

            steps[3].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[3].status = "completed"
            pages_label = "page" if metrics.page_count == 1 else "pages"
            steps[3].message = f"{metrics.page_count} {pages_label}, {metrics.total_words:,} words across document"

            # -------------------------------------------------------------
            # STEP 5: Prepare Visual Previews
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[4].status = "running"

            # Check RenderCV's generated PNGs
            png_files = sorted(out_folder.glob("*.png"))
            preview_urls = []

            # If RenderCV generated PNGs per page, copy them to session_dir
            if png_files:
                for idx, png in enumerate(png_files):
                    target_png = session_dir / f"page_{idx + 1}.png"
                    shutil.copy2(png, target_png)
                    preview_urls.append(f"/api/preview/{token}/page/{idx + 1}")
            else:
                # Fallback to pdftoppm if available
                try:
                    subprocess.run(
                        ["pdftoppm", "-png", "-r", "150", str(session_pdf), str(session_dir / "page")],
                        check=True,
                        capture_output=True,
                    )
                    gen_pngs = sorted(session_dir.glob("page-*.png"))
                    for idx, png in enumerate(gen_pngs):
                        dest = session_dir / f"page_{idx + 1}.png"
                        if png != dest:
                            shutil.move(png, dest)
                        preview_urls.append(f"/api/preview/{token}/page/{idx + 1}")
                except Exception as e:
                    pass

            response.preview_urls = preview_urls
            response.pdf_preview_url = f"/api/preview/{token}/pdf"

            steps[4].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[4].status = "completed"
            steps[4].message = f"Ready for review: {len(preview_urls)} high-resolution page preview(s)"

            response.success = True
            response.cli_logs = "\n\n".join(cli_logs)
            return response

        except Exception as e:
            response.error = f"Unexpected error during rendering: {str(e)}"
            for step in steps:
                if step.status == "running":
                    step.status = "failed"
                    step.message = str(e)
            response.cli_logs = "\n\n".join(cli_logs)
            return response

    def save_resume(
        self,
        token: str,
        custom_filename: Optional[str] = None,
        save_directory: Optional[str] = None,
    ) -> SaveResponse:
        """
        Saves the rendered PDF from session cache to the requested location.
        """
        session_dir = self.cache_dir / token
        session_pdf = session_dir / "resume.pdf"

        if not session_pdf.exists():
            return SaveResponse(
                success=False,
                saved_path="",
                message="Rendered PDF session expired or not found.",
                error="Session PDF does not exist. Please render again.",
            )

        target_dir_str = save_directory or DEFAULT_SAVE_DIR
        target_dir = Path(os.path.expanduser(target_dir_str)).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = custom_filename or "VinayakPastey_Resume.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        destination_file = target_dir / filename

        try:
            shutil.copy2(session_pdf, destination_file)
            return SaveResponse(
                success=True,
                saved_path=str(destination_file),
                message=f"Resume successfully accepted and saved to {destination_file}",
            )
        except Exception as e:
            return SaveResponse(
                success=False,
                saved_path="",
                message=f"Failed to save file: {str(e)}",
                error=str(e),
            )
