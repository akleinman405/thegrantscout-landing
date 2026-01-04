"""Configuration package for TheGrantScout Pipeline."""
from .database import init_pool, get_connection, query_df
from .settings import (
    PROJECT_ROOT, DATA_DIR, OUTPUT_DIR, CACHE_DIR, LOG_DIR, QUESTIONNAIRE_DIR,
    ANTHROPIC_API_KEY, CACHE_TTL_DAYS, LOG_LEVEL
)

__all__ = [
    'init_pool', 'get_connection', 'query_df',
    'PROJECT_ROOT', 'DATA_DIR', 'OUTPUT_DIR', 'CACHE_DIR', 'LOG_DIR', 'QUESTIONNAIRE_DIR',
    'ANTHROPIC_API_KEY', 'CACHE_TTL_DAYS', 'LOG_LEVEL'
]
