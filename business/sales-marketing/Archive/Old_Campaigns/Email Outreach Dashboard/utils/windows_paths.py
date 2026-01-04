"""
Windows path utilities for the Campaign Control Center.
Centralizes all file path handling for cross-platform compatibility.
"""

import os
import sys
from typing import Optional


# Detect if running on WSL and convert paths accordingly
def _get_base_directory():
    """Detect environment and return appropriate base directory."""
    # Check if running on WSL
    if sys.platform == 'linux' and os.path.exists('/mnt/c'):
        # WSL path
        return r"/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences"
    else:
        # Windows path
        return r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"


# Base directory for all campaign files
BASE_DIR = r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences"


def get_base_dir() -> str:
    """
    Get the base directory for all campaign files.

    Returns:
        str: Base directory path (Windows format)
    """
    return BASE_DIR


def get_database_path() -> str:
    """
    Get the path to the SQLite database file.

    Returns:
        str: Full path to campaign_control.db
    """
    return os.path.join(BASE_DIR, "Email Outreach Dashboard", "campaign_control.db")


def get_vertical_csv_path(vertical_id: str) -> str:
    """
    Get the path to a vertical's prospects CSV file.

    Args:
        vertical_id: The vertical identifier (e.g., 'debarment', 'food_recall')

    Returns:
        str: Full path to the vertical's CSV file
    """
    filename = f"{vertical_id}_prospects.csv"
    return os.path.join(BASE_DIR, filename)


def get_sent_tracker_path() -> str:
    """
    Get the path to the sent emails tracker CSV.

    Returns:
        str: Full path to sent_tracker.csv
    """
    return os.path.join(BASE_DIR, "sent_tracker.csv")


def get_response_tracker_path() -> str:
    """
    Get the path to the response tracker CSV.

    Returns:
        str: Full path to response_tracker.csv
    """
    return os.path.join(BASE_DIR, "response_tracker.csv")


def get_coordination_path() -> str:
    """
    Get the path to the coordination JSON file.

    Returns:
        str: Full path to coordination.json
    """
    return os.path.join(BASE_DIR, "coordination.json")


def get_error_log_path() -> str:
    """
    Get the path to the error log CSV.

    Returns:
        str: Full path to error_log.csv
    """
    return os.path.join(BASE_DIR, "error_log.csv")


def get_template_directory(vertical_id: str) -> str:
    """
    Get the directory for storing email templates for a vertical.

    Args:
        vertical_id: The vertical identifier

    Returns:
        str: Full path to the templates directory
    """
    templates_dir = os.path.join(BASE_DIR, "templates", vertical_id)
    # Ensure directory exists
    os.makedirs(templates_dir, exist_ok=True)
    return templates_dir


def get_template_file_path(vertical_id: str, template_type: str, template_name: str) -> str:
    """
    Get the full path to a specific template file.

    Args:
        vertical_id: The vertical identifier
        template_type: 'initial' or 'followup'
        template_name: Name of the template

    Returns:
        str: Full path to the template file
    """
    templates_dir = get_template_directory(vertical_id)
    filename = f"{template_type}_{template_name}.txt"
    return os.path.join(templates_dir, filename)


def join_path(*parts: str) -> str:
    """
    Join path components using os.path.join for Windows compatibility.

    Args:
        *parts: Path components to join

    Returns:
        str: Joined path
    """
    return os.path.join(*parts)


def normalize_path(path: str) -> str:
    """
    Normalize a path to use the correct separators for the current OS.

    Args:
        path: Path to normalize

    Returns:
        str: Normalized path
    """
    return os.path.normpath(path)


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: Directory path to create
    """
    os.makedirs(path, exist_ok=True)


def get_dashboard_base_dir() -> str:
    """
    Get the base directory for the dashboard application.

    Returns:
        str: Dashboard application directory
    """
    return os.path.join(BASE_DIR, "Email Outreach Dashboard")


def file_exists(path: str) -> bool:
    """
    Check if a file exists at the given path.

    Args:
        path: File path to check

    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.exists(path) and os.path.isfile(path)


def directory_exists(path: str) -> bool:
    """
    Check if a directory exists at the given path.

    Args:
        path: Directory path to check

    Returns:
        bool: True if directory exists, False otherwise
    """
    return os.path.exists(path) and os.path.isdir(path)
