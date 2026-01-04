"""
Centralized settings module for TheGrantScout Pipeline.

Loads configuration from environment variables and .env file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'
CACHE_DIR = DATA_DIR / 'cache'
LOG_DIR = OUTPUT_DIR / 'logs'
QUESTIONNAIRE_DIR = DATA_DIR / 'questionnaires'

# Also support questionnaires from beta testing folder
BETA_QUESTIONNAIRE_DIR = PROJECT_ROOT.parent / '2. Beta Testing'

# API settings
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Cache settings
CACHE_TTL_DAYS = int(os.getenv('CACHE_TTL_DAYS', '7'))

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Database settings (for reference, actual connection in database.py)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'thegrantscout')
DB_USER = os.getenv('DB_USER', 'postgres')

# Ensure directories exist
for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR, LOG_DIR, QUESTIONNAIRE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
