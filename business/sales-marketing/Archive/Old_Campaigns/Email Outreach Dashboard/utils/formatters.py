"""
Data formatting utilities for the Campaign Control Center.
Provides consistent formatting across the application.
"""

from datetime import datetime, timedelta
from typing import Optional, Union


def format_number(num: Union[int, float]) -> str:
    """
    Format a number with thousands separators.

    Args:
        num: Number to format

    Returns:
        str: Formatted number (e.g., "1,234")
    """
    if num is None:
        return "0"

    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal value as a percentage.

    Args:
        value: Decimal value (e.g., 0.125 for 12.5%)
        decimals: Number of decimal places

    Returns:
        str: Formatted percentage (e.g., "12.5%")
    """
    if value is None:
        return "0.0%"

    try:
        return f"{value * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_datetime(dt: Union[datetime, str], format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format a datetime object or string.

    Args:
        dt: Datetime object or ISO format string
        format: Format string for output

    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        return ""

    try:
        if isinstance(dt, str):
            # Try to parse ISO format
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

        return dt.strftime(format)
    except (ValueError, AttributeError, TypeError):
        return str(dt)


def format_date(dt: Union[datetime, str]) -> str:
    """
    Format a datetime as a date string.

    Args:
        dt: Datetime object or ISO format string

    Returns:
        str: Formatted date (e.g., "Nov 04, 2025")
    """
    return format_datetime(dt, format='%b %d, %Y')


def format_time_ago(dt: Union[datetime, str]) -> str:
    """
    Format a datetime as a relative time string.

    Args:
        dt: Datetime object or ISO format string

    Returns:
        str: Relative time string (e.g., "2 hours ago", "3 days ago")
    """
    if dt is None:
        return "Never"

    try:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

        # Make dt timezone-naive if it's timezone-aware
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)

        now = datetime.now()
        diff = now - dt

        # Future dates
        if diff.total_seconds() < 0:
            return "In the future"

        # Less than 1 minute
        if diff.total_seconds() < 60:
            seconds = int(diff.total_seconds())
            return f"{seconds} second{'s' if seconds != 1 else ''} ago"

        # Less than 1 hour
        if diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

        # Less than 1 day
        if diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

        # Less than 1 week
        if diff.days < 7:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"

        # Less than 1 month
        if diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"

        # Less than 1 year
        if diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"

        # Over a year
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"

    except (ValueError, AttributeError, TypeError):
        return str(dt)


def format_quota(used: int, total: int) -> str:
    """
    Format a quota display.

    Args:
        used: Number used
        total: Total available

    Returns:
        str: Formatted quota (e.g., "45 / 100 (45%)")
    """
    if total == 0:
        return f"{used} / {total} (0%)"

    percentage = (used / total) * 100
    return f"{used:,} / {total:,} ({percentage:.1f}%)"


def format_vertical_name(vertical_id: str) -> str:
    """
    Format a vertical ID into a display name.

    Args:
        vertical_id: Vertical identifier (e.g., "food_recall", "debarment")

    Returns:
        str: Formatted display name (e.g., "Food Recall", "Debarment")
    """
    if not vertical_id:
        return ""

    # Replace underscores with spaces and title case
    return vertical_id.replace('_', ' ').title()


def truncate_text(text: str, length: int, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if not text:
        return ""

    if len(text) <= length:
        return text

    return text[:length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration (e.g., "2h 30m", "45s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"


def format_status_badge(status: str) -> str:
    """
    Format a status string with emoji/icon.

    Args:
        status: Status string (e.g., 'active', 'paused', 'error')

    Returns:
        str: Formatted status with icon
    """
    status_lower = status.lower() if status else ''

    status_map = {
        'active': '✅ Active',
        'inactive': '⏸️ Inactive',
        'paused': '⏸️ Paused',
        'running': '▶️ Running',
        'stopped': '⏹️ Stopped',
        'idle': '⏸️ Idle',
        'error': '❌ Error',
        'success': '✅ Success',
        'pending': '⏳ Pending',
        'completed': '✅ Completed',
    }

    return status_map.get(status_lower, status)
