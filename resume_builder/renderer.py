"""
Renderer module for resume_builder.
Orchestrates YAML preprocessing, RenderCV CLI execution, step tracking,
PDF analytics, preview caching, and final file commitment.
Supports both Resume and Cover Letter generation.
"""

import os
import re
import shutil
import subprocess
import sys
import time
import uuid
import types
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, get_args, get_origin
from pydantic import BaseModel
from ruamel.yaml import YAML

# RenderCV Data Models for default configuration expansion
try:
    from rendercv.schema.models.locale.locale import EnglishLocale as Locale
    from rendercv.schema.models.settings.settings import Settings as RenderCVSettings
    from rendercv.schema.models.design.classic_theme import ClassicTheme
    from rendercv.schema.models.design.built_in_design import discover_other_themes

    available_theme_options = {
        cls.model_fields["theme"].default: cls
        for cls in [ClassicTheme, *discover_other_themes()]
    }
except ImportError:
    base_dir = Path(__file__).resolve().parent.parent
    venv_lib = base_dir / ".venv" / "lib"
    if venv_lib.exists():
        for site in venv_lib.glob("python*/site-packages"):
            if site.exists() and str(site) not in sys.path:
                sys.path.insert(0, str(site))
    try:
        from rendercv.schema.models.locale.locale import EnglishLocale as Locale
        from rendercv.schema.models.settings.settings import Settings as RenderCVSettings
        from rendercv.schema.models.design.classic_theme import ClassicTheme
        from rendercv.schema.models.design.built_in_design import discover_other_themes

        available_theme_options = {
            cls.model_fields["theme"].default: cls
            for cls in [ClassicTheme, *discover_other_themes()]
        }
    except ImportError:
        try:
            from rendercv.data.models import Locale, RenderCVSettings, available_theme_options  # type: ignore
        except ImportError:
            available_theme_options = None
            Locale = None
            RenderCVSettings = None

from .analyzer import analyze_pdf
from .config import (
    CACHE_DIR,
    DEFAULT_FILENAME_PATTERN,
    DEFAULT_SAVE_DIR,
    DEFAULT_COVER_LETTER_SAVE_DIR,
)
from .models import DesignSettings, RenderResponse, SaveResponse, StepInfo


def deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merges override dictionary into base dictionary.
    Returns a new merged dictionary without mutating inputs.
    """
    if not isinstance(base, dict):
        return override if isinstance(override, dict) else {}
    if not isinstance(override, dict):
        return dict(base) if isinstance(base, dict) else {}

    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def get_base_model_class(annotation):
    """
    Extracts the underlying BaseModel subclass from a type annotation,
    handling Union and Optional annotations if necessary.
    """
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        for arg in get_args(annotation):
            if isinstance(arg, type) and issubclass(arg, BaseModel):
                return arg
    return None


def filter_to_model(model_cls, data: dict) -> dict:
    """
    Recursively filters a dictionary so it contains only keys and sub-keys
    defined in model_cls's Pydantic schema, preventing extra_forbidden validation errors.
    """
    if not isinstance(data, dict) or not hasattr(model_cls, "model_fields"):
        return data
    result = {}
    for k, v in data.items():
        if k in model_cls.model_fields:
            field_info = model_cls.model_fields[k]
            sub_cls = get_base_model_class(field_info.annotation)
            if sub_cls and isinstance(v, dict):
                result[k] = filter_to_model(sub_cls, v)
            else:
                result[k] = v
    return result


def sanitize_name(name: str) -> str:
    """
    Sanitizes role and company names for safe, clean filenames.
    Replaces whitespace, slashes, and non-alphanumeric chars with single underscores.
    """
    if not name:
        return ""
    name = re.sub(r"[^\w]+", "_", name.strip())
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
            "--output-folder",
            output_dir_name,
            "--dont-generate-markdown",
            "--dont-generate-html",
        ]
    elif venv_rcv.exists():
        cmd = [
            str(venv_rcv),
            "render",
            str(input_yaml_path),
            "--output-folder",
            output_dir_name,
            "--dont-generate-markdown",
            "--dont-generate-html",
        ]
    elif shutil.which("rendercv"):
        cmd = [
            shutil.which("rendercv"),
            "render",
            str(input_yaml_path),
            "--output-folder",
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
            "--output-folder",
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


def build_cover_letter_filename(
    role: str = "", company: str = "", custom_name: Optional[str] = None
) -> str:
    """
    Constructs the final cover letter filename corresponding to the resume.
    Defaults to: VinayakPastey_Cover_Letter_<role-name>_<company-name>.pdf
    """
    if custom_name and custom_name.strip():
        name = custom_name.strip()
        stem = Path(name).stem
        if "Resume" in stem:
            return stem.replace("Resume", "Cover_Letter") + ".pdf"
        return f"{stem}_Cover_Letter.pdf"

    clean_role = sanitize_name(role)
    clean_company = sanitize_name(company)

    if clean_role and clean_company:
        return f"VinayakPastey_Cover_Letter_{clean_role}_{clean_company}.pdf"
    elif clean_role:
        return f"VinayakPastey_Cover_Letter_{clean_role}.pdf"
    elif clean_company:
        return f"VinayakPastey_Cover_Letter_{clean_company}.pdf"
    else:
        return "VinayakPastey_Cover_Letter.pdf"


def resolve_save_path(save_dir: str, filename: str) -> Path:
    """
    Expands home path (e.g. ~/Documents/Globathon/Resumes) and joins filename.
    """
    expanded = os.path.expanduser(save_dir)
    return Path(expanded) / filename


def patch_rendercv_typst_template():
    """
    RenderCV compatibility hook.
    """
    try:
        import rendercv

        rcv_dir = Path(rendercv.__file__).parent / "themes"
        if not rcv_dir.exists():
            return
        target_str = 'if type(page.margin) == "dictionary" {'
        replacement_str = (
            'if type(page.margin) == dictionary or type(page.margin) == "dictionary" {'
        )
        for preamble in rcv_dir.glob("**/Preamble.j2.typ"):
            content = preamble.read_text(encoding="utf-8")
            if target_str in content:
                content = content.replace(target_str, replacement_str)
                preamble.write_text(content, encoding="utf-8")
    except Exception:
        pass


patch_rendercv_typst_template()


class ResumeRenderer:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        patch_rendercv_typst_template()

    def render_resume(
        self,
        yaml_content: str,
        company_name: str = "",
        role_name: str = "",
        custom_filename: Optional[str] = None,
        custom_cover_letter_filename: Optional[str] = None,
        save_directory: str = DEFAULT_SAVE_DIR,
        cover_letter_save_directory: str = DEFAULT_COVER_LETTER_SAVE_DIR,
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
                description="Parse syntax and check resume & cover letter data structure",
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
        if custom_cover_letter_filename and custom_cover_letter_filename.strip():
            cl_name = custom_cover_letter_filename.strip()
            if not cl_name.lower().endswith(".pdf"):
                cl_name += ".pdf"
            resolved_cl_filename = cl_name
        else:
            resolved_cl_filename = build_cover_letter_filename(
                role_name, company_name, resolved_filename
            )

        response = RenderResponse(
            token=token,
            success=False,
            steps=steps,
            resolved_filename=resolved_filename,
            cover_letter_resolved_filename=resolved_cl_filename,
            save_directory=save_directory,
            cover_letter_save_directory=cover_letter_save_directory,
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

            if not isinstance(data, dict) or ("cv" not in data and "cover_letter" not in data):
                steps[0].status = "failed"
                steps[0].message = "Missing root 'cv' or 'cover_letter' section in YAML."
                response.error = "Invalid RenderCV YAML: Missing top-level 'cv' or 'cover_letter' key."
                return response

            has_cl_in_input = "cover_letter" in data and isinstance(data["cover_letter"], dict)

            steps[0].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[0].status = "completed"
            applicant_name = (
                data.get("cv", {}).get("name")
                or data.get("cover_letter", {}).get("name")
                or "Applicant"
            )
            cl_label = " + Cover Letter" if has_cl_in_input else ""
            steps[0].message = f"Successfully parsed spec for '{applicant_name}'{cl_label}"

            # -------------------------------------------------------------
            # STEP 2: Apply Design, Settings, Locale & Defaults
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[1].status = "running"

            # 1. Clean up legacy root-level or cv-level keys
            if "cv" in data and isinstance(data["cv"], dict):
                data["cv"].pop("sort_entries", None)
            data.pop("sort_entries", None)

            # 2. Expand & Sanitize Settings Defaults
            default_settings = {}
            if RenderCVSettings:
                default_settings = RenderCVSettings().model_dump(mode="json", exclude_none=True)

            user_raw_settings = data.pop("settings", {})
            if not isinstance(user_raw_settings, dict):
                user_raw_settings = {}
            user_rcv_settings = data.pop("rendercv_settings", {})
            if not isinstance(user_rcv_settings, dict):
                user_rcv_settings = {}

            merged_settings = deep_merge(
                default_settings, deep_merge(user_rcv_settings, user_raw_settings)
            )
            if "date" in merged_settings and "current_date" not in user_raw_settings:
                merged_settings["current_date"] = merged_settings.pop("date")

            if RenderCVSettings:
                data["settings"] = filter_to_model(RenderCVSettings, merged_settings)
            else:
                data["settings"] = merged_settings

            # 3. Expand & Sanitize Locale
            if "locale" in data and isinstance(data["locale"], dict):
                if data["locale"].get("language") == "en":
                    data["locale"]["language"] = "english"
                data["locale"].pop("phone_number_format", None)
                if Locale:
                    data["locale"] = filter_to_model(Locale, data["locale"])

            # 4. Expand, Override & Sanitize Design
            theme_cls = None
            if available_theme_options:
                theme_cls = available_theme_options.get(design.theme)
                if not theme_cls:
                    theme_cls = available_theme_options.get(
                        "engineeringresumes"
                    ) or available_theme_options.get("classic")

            default_design = {}
            if theme_cls:
                default_design = theme_cls().model_dump(mode="json", exclude_none=True)

            user_design = data.get("design")
            if not isinstance(user_design, dict):
                user_design = {}

            # Migrate legacy 2.3 design keys in user_design if present
            if "text" in user_design and isinstance(user_design["text"], dict):
                if "font_family" in user_design["text"]:
                    user_design.setdefault("typography", {})["font_family"] = user_design[
                        "text"
                    ]["font_family"]
            if "section_titles" in user_design and isinstance(
                user_design["section_titles"], dict
            ):
                if "type" in user_design["section_titles"] and isinstance(
                    user_design["section_titles"]["type"], str
                ):
                    user_design["section_titles"]["type"] = user_design[
                        "section_titles"
                    ]["type"].replace("-", "_")
            if "colors" in user_design and isinstance(user_design["colors"], dict):
                if "text" in user_design["colors"]:
                    user_design["colors"]["body"] = user_design["colors"]["text"]
                if "last_updated_date_and_page_numbering" in user_design["colors"]:
                    lup = user_design["colors"]["last_updated_date_and_page_numbering"]
                    user_design["colors"].setdefault("footer", lup)
                    user_design["colors"].setdefault("top_note", lup)
            if "links" in user_design and isinstance(user_design["links"], dict):
                if "use_external_link_icon" in user_design["links"]:
                    user_design["links"]["show_external_link_icon"] = user_design[
                        "links"
                    ]["use_external_link_icon"]
            if "page" in user_design and isinstance(user_design["page"], dict):
                if "show_page_numbering" in user_design["page"]:
                    user_design["page"]["show_footer"] = user_design["page"][
                        "show_page_numbering"
                    ]
                if "show_last_updated_date" in user_design["page"]:
                    user_design["page"]["show_top_note"] = user_design["page"][
                        "show_last_updated_date"
                    ]
            if "entries" in user_design and isinstance(user_design["entries"], dict):
                if "allow_page_break_in_entries" in user_design["entries"]:
                    user_design["entries"]["allow_page_break"] = user_design["entries"][
                        "allow_page_break_in_entries"
                    ]
                if "allow_page_break_in_sections" in user_design["entries"]:
                    user_design.setdefault("sections", {})["allow_page_break"] = (
                        user_design["entries"]["allow_page_break_in_sections"]
                    )

            merged_design = deep_merge(default_design, user_design)

            # Apply UI Design overrides
            merged_design["theme"] = design.theme

            if "page" not in merged_design or not isinstance(merged_design["page"], dict):
                merged_design["page"] = {}
            merged_design["page"]["size"] = design.page_size

            # Footer / Top note handling
            if design.no_footer_or_top_note:
                merged_design["page"]["show_footer"] = False
                merged_design["page"]["show_top_note"] = False
                merged_design.setdefault("templates", {})["footer"] = ""
                merged_design.setdefault("templates", {})["top_note"] = ""
            else:
                if design.show_page_numbering is not None:
                    merged_design["page"]["show_footer"] = design.show_page_numbering
                if design.show_last_updated_date is not None:
                    merged_design["page"]["show_top_note"] = design.show_last_updated_date

            # Font settings (apply to all font slots via typography.font_family)
            merged_design.setdefault("typography", {})["font_family"] = design.font_family

            # Phone number format is under design.header.connections in RenderCV 2.8+
            merged_design.setdefault("header", {}).setdefault(
                "connections", {}
            )["phone_number_format"] = design.phone_number_format

            # Entry & Section page breaks
            merged_design.setdefault("entries", {})["allow_page_break"] = (
                design.allow_page_break_in_entries
            )
            merged_design.setdefault("sections", {})["allow_page_break"] = (
                design.allow_page_break_in_sections
            )

            # Filter merged_design to ensure strict RenderCV schema validity
            if theme_cls:
                data["design"] = filter_to_model(theme_cls, merged_design)
            else:
                data["design"] = merged_design

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

            # Differentiate Resume PDF vs Cover Letter PDF
            cover_letter_pdfs = [p for p in pdf_files if "Cover_Letter" in p.name]
            resume_pdfs = [p for p in pdf_files if "Cover_Letter" not in p.name]

            resume_pdf_file = resume_pdfs[0] if resume_pdfs else pdf_files[0]
            session_pdf = session_dir / "resume.pdf"
            shutil.copy2(resume_pdf_file, session_pdf)

            has_cover_letter = False
            session_cl_pdf = session_dir / "cover_letter.pdf"
            if cover_letter_pdfs:
                has_cover_letter = True
                shutil.copy2(cover_letter_pdfs[0], session_cl_pdf)

            steps[2].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[2].status = "completed"
            summary_label = (
                f"Rendered CV + Cover Letter ({resume_pdf_file.stat().st_size // 1024} KB)"
                if has_cover_letter
                else f"Rendered CV ({resume_pdf_file.stat().st_size // 1024} KB)"
            )
            steps[2].message = summary_label

            # -------------------------------------------------------------
            # STEP 4: Analyze Metrics
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[3].status = "running"

            metrics = analyze_pdf(session_pdf)
            response.metrics = metrics

            if has_cover_letter and session_cl_pdf.exists():
                response.cover_letter_metrics = analyze_pdf(session_cl_pdf)

            steps[3].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[3].status = "completed"
            pages_label = "page" if metrics.page_count == 1 else "pages"
            steps[3].message = f"{metrics.page_count} {pages_label}, {metrics.total_words:,} words across document"

            # -------------------------------------------------------------
            # STEP 5: Prepare Visual Previews
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            steps[4].status = "running"

            preview_urls = []
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
            except Exception:
                # Fallback to RenderCV generated PNGs if pdftoppm not available
                png_files = sorted(out_folder.glob("*.png"))
                for idx, png in enumerate(png_files):
                    dest = session_dir / f"page_{idx + 1}.png"
                    shutil.copy2(png, dest)
                    preview_urls.append(f"/api/preview/{token}/page/{idx + 1}")

            response.preview_urls = preview_urls
            response.pdf_preview_url = f"/api/preview/{token}/pdf"

            # Generate Cover Letter Previews if present
            if has_cover_letter and session_cl_pdf.exists():
                cl_preview_urls = []
                try:
                    subprocess.run(
                        [
                            "pdftoppm",
                            "-png",
                            "-r",
                            "150",
                            str(session_cl_pdf),
                            str(session_dir / "cl_page"),
                        ],
                        check=True,
                        capture_output=True,
                    )
                    gen_cl_pngs = sorted(session_dir.glob("cl_page-*.png"))
                    for idx, png in enumerate(gen_cl_pngs):
                        dest = session_dir / f"cover_letter_page_{idx + 1}.png"
                        if png != dest:
                            shutil.move(png, dest)
                        cl_preview_urls.append(
                            f"/api/preview/{token}/cover-letter-page/{idx + 1}"
                        )
                except Exception:
                    pass

                response.has_cover_letter = True
                response.cover_letter_preview_urls = cl_preview_urls
                response.cover_letter_pdf_url = f"/api/preview/{token}/cover-letter-pdf"

            steps[4].duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            steps[4].status = "completed"
            ready_msg = f"Ready for review: {len(preview_urls)} page(s)"
            if has_cover_letter:
                ready_msg += f" + Cover Letter ({len(response.cover_letter_preview_urls)} page)"
            steps[4].message = ready_msg

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
        custom_cover_letter_filename: Optional[str] = None,
        save_directory: Optional[str] = None,
        cover_letter_save_directory: Optional[str] = None,
        save_resume: bool = True,
        save_cover_letter: bool = False,
    ) -> SaveResponse:
        """
        Saves the rendered PDF and/or cover letter PDF from session cache to the requested locations.
        Only saves documents that are explicitly requested.
        """
        session_dir = self.cache_dir / token
        session_pdf = session_dir / "resume.pdf"
        session_cl_pdf = session_dir / "cover_letter.pdf"

        # If neither flag is True, default to saving resume
        if not save_resume and not save_cover_letter:
            save_resume = True

        saved_path = ""
        saved_cl_path: Optional[str] = None
        messages = []

        try:
            if save_resume:
                if not session_pdf.exists():
                    return SaveResponse(
                        success=False,
                        saved_path="",
                        message="Rendered Resume PDF not found or session expired.",
                        error="Session resume PDF does not exist. Please render again.",
                    )
                target_dir_str = save_directory or DEFAULT_SAVE_DIR
                target_dir = Path(os.path.expanduser(target_dir_str)).resolve()
                target_dir.mkdir(parents=True, exist_ok=True)

                filename = custom_filename or "VinayakPastey_Resume.pdf"
                if not filename.lower().endswith(".pdf"):
                    filename += ".pdf"

                destination_file = target_dir / filename
                shutil.copy2(session_pdf, destination_file)
                saved_path = str(destination_file)
                messages.append(f"Resume saved to {destination_file}")

            if save_cover_letter:
                if not session_cl_pdf.exists():
                    return SaveResponse(
                        success=False,
                        saved_path=saved_path,
                        message="Rendered Cover Letter PDF not found or session expired.",
                        error="Session cover letter PDF does not exist. Please render again.",
                    )
                cl_target_dir_str = (
                    cover_letter_save_directory or DEFAULT_COVER_LETTER_SAVE_DIR
                )
                cl_target_dir = Path(os.path.expanduser(cl_target_dir_str)).resolve()
                cl_target_dir.mkdir(parents=True, exist_ok=True)

                cl_filename = custom_cover_letter_filename or build_cover_letter_filename(
                    custom_name=custom_filename
                )
                if not cl_filename.lower().endswith(".pdf"):
                    cl_filename += ".pdf"

                cl_destination = cl_target_dir / cl_filename
                shutil.copy2(session_cl_pdf, cl_destination)
                saved_cl_path = str(cl_destination)
                messages.append(f"Cover letter saved to {cl_destination}")

            return SaveResponse(
                success=True,
                saved_path=saved_path,
                saved_cover_letter_path=saved_cl_path,
                message="\n".join(messages),
            )
        except Exception as e:
            return SaveResponse(
                success=False,
                saved_path=saved_path,
                saved_cover_letter_path=saved_cl_path,
                message=f"Failed to save file: {str(e)}",
                error=str(e),
            )
