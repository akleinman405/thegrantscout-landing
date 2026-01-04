"""
Utilities package for Campaign Control Center.
Provides path handling, validation, and formatting functions.
"""

# Path utilities
from .windows_paths import (
    get_base_dir,
    get_database_path,
    get_vertical_csv_path,
    get_sent_tracker_path,
    get_response_tracker_path,
    get_coordination_path,
    get_error_log_path,
    get_template_directory,
    get_template_file_path,
    join_path,
    normalize_path,
    ensure_directory_exists,
    get_dashboard_base_dir,
    file_exists,
    directory_exists
)

# Validators
from .validators import (
    validate_email,
    validate_csv_schema,
    validate_vertical_id,
    sanitize_filename,
    validate_prospect_csv,
    validate_file_upload,
    validate_smtp_settings,
    validate_template_content,
    validate_daily_limit
)

# Formatters
from .formatters import (
    format_number,
    format_percentage,
    format_datetime,
    format_date,
    format_time_ago,
    format_quota,
    format_vertical_name,
    truncate_text,
    format_file_size,
    format_duration,
    format_status_badge
)

__all__ = [
    # Path utilities
    'get_base_dir',
    'get_database_path',
    'get_vertical_csv_path',
    'get_sent_tracker_path',
    'get_response_tracker_path',
    'get_coordination_path',
    'get_error_log_path',
    'get_template_directory',
    'get_template_file_path',
    'join_path',
    'normalize_path',
    'ensure_directory_exists',
    'get_dashboard_base_dir',
    'file_exists',
    'directory_exists',
    # Validators
    'validate_email',
    'validate_csv_schema',
    'validate_vertical_id',
    'sanitize_filename',
    'validate_prospect_csv',
    'validate_file_upload',
    'validate_smtp_settings',
    'validate_template_content',
    'validate_daily_limit',
    # Formatters
    'format_number',
    'format_percentage',
    'format_datetime',
    'format_date',
    'format_time_ago',
    'format_quota',
    'format_vertical_name',
    'truncate_text',
    'format_file_size',
    'format_duration',
    'format_status_badge'
]
