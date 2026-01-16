"""
TheGrantScout utilities package.
"""
from .paths import (
    get_project_root,
    get_db_host,
    get_db_config,
    get_credentials_password,
    get_database_dir,
    get_credentials_file,
    get_embeddings_dir,
    get_reports_dir,
    get_admin_dir,
)

__all__ = [
    'get_project_root',
    'get_db_host',
    'get_db_config',
    'get_credentials_password',
    'get_database_dir',
    'get_credentials_file',
    'get_embeddings_dir',
    'get_reports_dir',
    'get_admin_dir',
]
