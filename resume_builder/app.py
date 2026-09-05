"""
FastAPI application for resume_builder.
"""

from pathlib import Path
import os
import sys

# Ensure local venv site-packages are loaded if running with system python
venv_site = Path(__file__).resolve().parent.parent / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    BASE_DIR,
    CACHE_DIR,
    DEFAULT_SAVE_DIR,
    DEFAULT_THEME,
    DEFAULT_PAGE_SIZE,
    DEFAULT_FONT,
    DEFAULT_PHONE_FORMAT,
    DEFAULT_ALLOW_PAGE_BREAK_IN_ENTRIES,
    DEFAULT_SHOW_PAGE_NUMBERING,
    DEFAULT_SHOW_LAST_UPDATED_DATE,
    AVAILABLE_THEMES,
    AVAILABLE_FONTS,
    AVAILABLE_PAGE_SIZES,
    AVAILABLE_PHONE_FORMATS,
)
from .models import DesignSettings, RenderRequest, RenderResponse, SaveRequest, SaveResponse
from .renderer import ResumeRenderer, build_filename

app = FastAPI(
    title="Resume Builder",
    description="Modern RenderCV UI with live steps, PDF metrics, and preview",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SAMPLE_YAML_PATH = Path(__file__).resolve().parent / "samples" / "sample_resume.yaml"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
renderer = ResumeRenderer()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Renders the modern resume builder interface.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "default_save_dir": DEFAULT_SAVE_DIR,
            "default_theme": DEFAULT_THEME,
            "default_page_size": DEFAULT_PAGE_SIZE,
            "default_font": DEFAULT_FONT,
            "default_phone_format": DEFAULT_PHONE_FORMAT,
            "available_themes": AVAILABLE_THEMES,
            "available_fonts": AVAILABLE_FONTS,
            "available_page_sizes": AVAILABLE_PAGE_SIZES,
            "available_phone_formats": AVAILABLE_PHONE_FORMATS,
        },
    )


@app.get("/api/config")
async def get_config():
    """
    Returns initial configuration, themes, fonts, and defaults for frontend initialization.
    """
    return {
        "default_save_dir": DEFAULT_SAVE_DIR,
        "default_theme": DEFAULT_THEME,
        "default_page_size": DEFAULT_PAGE_SIZE,
        "default_font": DEFAULT_FONT,
        "default_phone_format": DEFAULT_PHONE_FORMAT,
        "default_allow_page_break": DEFAULT_ALLOW_PAGE_BREAK_IN_ENTRIES,
        "default_show_page_numbering": DEFAULT_SHOW_PAGE_NUMBERING,
        "default_show_last_updated": DEFAULT_SHOW_LAST_UPDATED_DATE,
        "available_themes": AVAILABLE_THEMES,
        "available_fonts": AVAILABLE_FONTS,
        "available_page_sizes": AVAILABLE_PAGE_SIZES,
        "available_phone_formats": AVAILABLE_PHONE_FORMATS,
    }


@app.get("/api/sample")
async def get_sample_resume():
    """
    Returns the bundled sample resume YAML content.
    """
    if SAMPLE_YAML_PATH.exists():
        content = SAMPLE_YAML_PATH.read_text(encoding="utf-8")
    elif (BASE_DIR / "Vinayak_Pastey_CV.yaml").exists():
        content = (BASE_DIR / "Vinayak_Pastey_CV.yaml").read_text(encoding="utf-8")
    else:
        content = "# RenderCV Resume\ncv:\n  name: Vinayak Pastey\n  location: Bengaluru, India\n"

    return {"yaml": content}


@app.post("/api/render", response_model=RenderResponse)
async def render_resume_endpoint(request: RenderRequest):
    """
    Parses YAML, sets design attributes, runs RenderCV CLI, extracts metrics, and creates previews.
    """
    res = renderer.render_resume(
        yaml_content=request.yaml_content,
        company_name=request.company_name,
        role_name=request.role_name,
        custom_filename=request.custom_filename,
        save_directory=request.save_directory,
        design=request.design,
    )
    return res


@app.post("/api/render-upload", response_model=RenderResponse)
async def render_upload_endpoint(
    file: UploadFile = File(...),
    company_name: str = Form(""),
    role_name: str = Form(""),
    custom_filename: str = Form(""),
    save_directory: str = Form(DEFAULT_SAVE_DIR),
    theme: str = Form(DEFAULT_THEME),
    font_family: str = Form(DEFAULT_FONT),
    page_size: str = Form(DEFAULT_PAGE_SIZE),
    no_footer_or_top_note: bool = Form(True),
    phone_number_format: str = Form(DEFAULT_PHONE_FORMAT),
    allow_page_break_in_entries: bool = Form(DEFAULT_ALLOW_PAGE_BREAK_IN_ENTRIES),
):
    """
    Accepts uploaded YAML file multipart form and triggers render pipeline.
    """
    content_bytes = await file.read()
    yaml_content = content_bytes.decode("utf-8")

    design = DesignSettings(
        theme=theme,
        font_family=font_family,
        page_size=page_size,
        no_footer_or_top_note=no_footer_or_top_note,
        phone_number_format=phone_number_format,
        allow_page_break_in_entries=allow_page_break_in_entries,
    )

    res = renderer.render_resume(
        yaml_content=yaml_content,
        company_name=company_name,
        role_name=role_name,
        custom_filename=custom_filename if custom_filename else None,
        save_directory=save_directory,
        design=design,
    )
    return res


@app.get("/api/preview/{token}/page/{page_num}")
async def get_preview_page(token: str, page_num: int):
    """
    Serves the rendered PNG image for a specific page.
    """
    image_path = CACHE_DIR / token / f"page_{page_num}.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Preview page image not found")
    return FileResponse(image_path, media_type="image/png")


@app.get("/api/preview/{token}/pdf")
async def get_preview_pdf(token: str):
    """
    Serves the rendered PDF file for download or direct browser viewing.
    """
    pdf_path = CACHE_DIR / token / "resume.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Rendered PDF file not found")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="resume.pdf",
    )


@app.post("/api/save", response_model=SaveResponse)
async def save_resume_endpoint(request: SaveRequest):
    """
    Commits the rendered resume PDF to the user's specified destination path.
    """
    res = renderer.save_resume(
        token=request.token,
        custom_filename=request.custom_filename,
        save_directory=request.save_directory,
    )
    if not res.success:
        raise HTTPException(status_code=400, detail=res.error or res.message)
    return res
