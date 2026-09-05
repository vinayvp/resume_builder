"""
Pydantic data models for Resume Builder.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .config import (
    DEFAULT_THEME,
    DEFAULT_PAGE_SIZE,
    DEFAULT_FONT,
    DEFAULT_PHONE_FORMAT,
    DEFAULT_ALLOW_PAGE_BREAK_IN_ENTRIES,
    DEFAULT_ALLOW_PAGE_BREAK_IN_SECTIONS,
    DEFAULT_SAVE_DIR,
)


class DesignSettings(BaseModel):
    theme: str = Field(default=DEFAULT_THEME, description="RenderCV theme name")
    font_family: str = Field(default=DEFAULT_FONT, description="Primary font family")
    page_size: str = Field(default=DEFAULT_PAGE_SIZE, description="Paper page size")
    no_footer_or_top_note: bool = Field(
        default=True,
        description="Disable both page numbers and last updated date (no footer or top note)"
    )
    show_page_numbering: Optional[bool] = Field(default=None)
    show_last_updated_date: Optional[bool] = Field(default=None)
    phone_number_format: str = Field(
        default=DEFAULT_PHONE_FORMAT,
        description="Phone number format: international, national, or E164"
    )
    allow_page_break_in_entries: bool = Field(
        default=DEFAULT_ALLOW_PAGE_BREAK_IN_ENTRIES,
        description="Allow page breaks within entry descriptions"
    )
    allow_page_break_in_sections: bool = Field(
        default=DEFAULT_ALLOW_PAGE_BREAK_IN_SECTIONS,
        description="Allow page breaks across section entries"
    )


class RenderRequest(BaseModel):
    yaml_content: str = Field(..., description="Raw YAML content of the resume")
    company_name: str = Field(default="", description="Target company name")
    role_name: str = Field(default="", description="Target role name")
    custom_filename: Optional[str] = Field(default=None, description="Custom override for output filename")
    save_directory: str = Field(default=DEFAULT_SAVE_DIR, description="Directory where resume will be saved")
    design: DesignSettings = Field(default_factory=DesignSettings, description="Design and formatting preferences")


class StepInfo(BaseModel):
    id: str
    name: str
    description: str
    status: str = "pending"  # "pending", "running", "completed", "failed"
    duration_ms: Optional[float] = None
    message: Optional[str] = None


class AnalysisResult(BaseModel):
    page_count: int = 0
    total_words: int = 0
    page_words: List[int] = Field(default_factory=list)
    character_count: int = 0


class RenderResponse(BaseModel):
    token: str
    success: bool
    error: Optional[str] = None
    steps: List[StepInfo] = Field(default_factory=list)
    metrics: Optional[AnalysisResult] = None
    preview_urls: List[str] = Field(default_factory=list)
    pdf_preview_url: str = ""
    resolved_filename: str = ""
    save_directory: str = ""
    cli_logs: str = ""


class SaveRequest(BaseModel):
    token: str
    custom_filename: Optional[str] = None
    save_directory: Optional[str] = None


class SaveResponse(BaseModel):
    success: bool
    saved_path: str
    message: str
    error: Optional[str] = None

