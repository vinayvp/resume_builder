"""
Configuration settings and defaults for resume_builder.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Default Save Location
DEFAULT_SAVE_DIR = "~/Documents/Globathon/Resumes"

# Default File Naming Template
DEFAULT_FILENAME_PATTERN = "VinayakPastey_Resume_{role}_{company}.pdf"

# Default Design Configuration
DEFAULT_THEME = "engineeringresumes"
DEFAULT_PAGE_SIZE = "a4"
DEFAULT_FONT = "Calibri"
DEFAULT_PHONE_FORMAT = "international"
DEFAULT_ALLOW_PAGE_BREAK_IN_ENTRIES = True
DEFAULT_ALLOW_PAGE_BREAK_IN_SECTIONS = True
DEFAULT_SHOW_PAGE_NUMBERING = False
DEFAULT_SHOW_LAST_UPDATED_DATE = False

# Available Theme Options in RenderCV
AVAILABLE_THEMES = [
    {"id": "engineeringresumes", "name": "Engineering Resumes (Default)"},
    {"id": "classic", "name": "Classic"},
    {"id": "engineeringclassic", "name": "Engineering Classic"},
    {"id": "moderncv", "name": "ModernCV"},
    {"id": "sb2nov", "name": "SB2Nov"},
]

# Available Font Options
AVAILABLE_FONTS = [
    "Calibri",
    "Source Sans 3",
    "Arial",
    "Roboto",
    "Lato",
    "Poppins",
    "EB Garamond",
    "Inter",
    "Montserrat",
    "Open Sans",
    "Raleway",
    "Times New Roman",
    "XCharter",
]

# Available Page Sizes
AVAILABLE_PAGE_SIZES = [
    {"id": "a4", "name": "A4 size (Default)"},
    {"id": "us-letter", "name": "US Letter"},
    {"id": "us-legal", "name": "US Legal"},
    {"id": "a3", "name": "A3 size"},
]

# Available Phone Formats
AVAILABLE_PHONE_FORMATS = [
    {"id": "international", "name": "International (+1 609 999 9995)"},
    {"id": "national", "name": "National (609-999-9995)"},
    {"id": "E164", "name": "E.164 (+16099999995)"},
]

# Workspace / Temp Directory for preview generations
CACHE_DIR = BASE_DIR / ".resume_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

