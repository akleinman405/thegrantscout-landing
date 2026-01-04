"""
Input validation functions for the Campaign Control Center.
Ensures data integrity and security.
"""

import re
from typing import Tuple, List, Optional
import pandas as pd


# Email validation regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    email = email.strip()
    if len(email) == 0 or len(email) > 254:  # RFC 5321
        return False

    return bool(re.match(EMAIL_REGEX, email))


def validate_csv_schema(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, str]:
    """
    Validate that a DataFrame has all required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty or None"

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"

    return True, ""


def validate_vertical_id(vertical_id: str) -> bool:
    """
    Validate vertical ID format.
    Must be alphanumeric with underscores only, no spaces or special characters.

    Args:
        vertical_id: Vertical identifier to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    if not vertical_id or not isinstance(vertical_id, str):
        return False

    # Allow alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(pattern, vertical_id):
        return False

    # Reasonable length limits
    if len(vertical_id) < 2 or len(vertical_id) > 50:
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and special character issues.

    Args:
        filename: Filename to sanitize

    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "unnamed"

    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove special characters, keep alphanumeric, underscore, hyphen, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Limit length
    max_length = 200
    if len(filename) > max_length:
        # Keep extension if present
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            base, ext = parts
            filename = base[:max_length - len(ext) - 1] + '.' + ext
        else:
            filename = filename[:max_length]

    # Prevent empty filename
    if not filename or filename.startswith('.'):
        filename = 'file_' + filename

    return filename


def validate_prospect_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate prospect CSV data.

    Args:
        df: DataFrame containing prospect data

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check required columns
    required_columns = ['email', 'first_name', 'company_name', 'state', 'website']
    is_valid, error = validate_csv_schema(df, required_columns)
    if not is_valid:
        return False, error

    # Validate email column has valid emails
    if 'email' in df.columns:
        invalid_emails = []
        for idx, email in df['email'].items():
            if pd.notna(email) and not validate_email(str(email)):
                invalid_emails.append(f"Row {idx + 2}: {email}")  # +2 for header and 0-indexing

        if invalid_emails:
            sample = invalid_emails[:5]  # Show first 5 errors
            error_msg = "Invalid email addresses found:\n" + "\n".join(sample)
            if len(invalid_emails) > 5:
                error_msg += f"\n... and {len(invalid_emails) - 5} more"
            return False, error_msg

    return True, ""


def validate_file_upload(
    file_size: int,
    filename: str,
    allowed_extensions: Optional[List[str]] = None,
    max_size_mb: int = 50
) -> Tuple[bool, str]:
    """
    Validate file upload parameters.

    Args:
        file_size: Size of file in bytes
        filename: Name of uploaded file
        allowed_extensions: List of allowed file extensions (e.g., ['.csv', '.txt'])
        max_size_mb: Maximum file size in MB

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"

    if file_size == 0:
        return False, "File is empty"

    # Check extension if specified
    if allowed_extensions:
        file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if file_ext not in [ext.lower() for ext in allowed_extensions]:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    # Basic security check - no executable extensions
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.ps1', '.dll', '.so']
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if file_ext in dangerous_extensions:
        return False, "Executable files are not allowed"

    return True, ""


def validate_smtp_settings(host: str, port: int, username: str) -> Tuple[bool, str]:
    """
    Validate SMTP settings (basic validation, not connection test).

    Args:
        host: SMTP server hostname
        port: SMTP server port
        username: SMTP username/email

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not host or not isinstance(host, str):
        return False, "SMTP host is required"

    if len(host.strip()) == 0:
        return False, "SMTP host cannot be empty"

    # Validate port
    if not isinstance(port, int):
        return False, "SMTP port must be a number"

    if port < 1 or port > 65535:
        return False, "SMTP port must be between 1 and 65535"

    # Common SMTP ports
    common_ports = [25, 465, 587, 2525]
    if port not in common_ports:
        # Warning, not error
        pass

    # Validate username (usually an email)
    if not username or not isinstance(username, str):
        return False, "SMTP username is required"

    if len(username.strip()) == 0:
        return False, "SMTP username cannot be empty"

    return True, ""


def validate_template_content(subject: str, body: str) -> Tuple[bool, str]:
    """
    Validate email template content.

    Args:
        subject: Email subject line
        body: Email body text

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not subject or len(subject.strip()) == 0:
        return False, "Subject line cannot be empty"

    if len(subject) > 200:
        return False, "Subject line is too long (max 200 characters)"

    if not body or len(body.strip()) == 0:
        return False, "Email body cannot be empty"

    if len(body) > 10000:
        return False, "Email body is too long (max 10,000 characters)"

    return True, ""


def validate_daily_limit(limit: int) -> Tuple[bool, str]:
    """
    Validate daily email sending limit.

    Args:
        limit: Daily sending limit

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(limit, int):
        return False, "Daily limit must be a number"

    if limit < 1:
        return False, "Daily limit must be at least 1"

    if limit > 2000:
        return False, "Daily limit cannot exceed 2000 (Gmail limit is ~500/day)"

    return True, ""
