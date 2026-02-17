"""
Application configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Google Sheets configuration
env_creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
if env_creds_path and env_creds_path.startswith(".."):
    # Convert relative path from app/ directory
    GOOGLE_CREDENTIALS_PATH = str(Path(__file__).parent.parent / "credentials" / "service_account.json")
else:
    GOOGLE_CREDENTIALS_PATH = env_creds_path or str(PROJECT_ROOT / "credentials" / "service_account.json")

SHEET_NAME = os.getenv("SHEET_NAME", "SkylarkData")
SHEET_ID = os.getenv("SHEET_ID", "")  # Optional: direct spreadsheet ID

# Server configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Mock data configuration
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "False").lower() == "true"
