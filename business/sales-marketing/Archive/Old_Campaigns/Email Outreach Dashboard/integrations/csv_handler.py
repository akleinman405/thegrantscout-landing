"""
CSV file operations for prospect management.
Handles reading, writing, and manipulation of prospect CSV files.
"""

import os
import pandas as pd
import tempfile
import shutil
from typing import Tuple, Dict, Optional
from contextlib import contextmanager

# Conditionally import fcntl (Unix only, not available on Windows)
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.windows_paths import get_vertical_csv_path
from utils.validators import validate_prospect_csv


# Required columns for prospect CSV files
REQUIRED_COLUMNS = ['email', 'first_name', 'company_name', 'state', 'website']


@contextmanager
def file_lock(file_path: str, mode: str = 'r'):
    """
    Context manager for file locking (thread-safe file operations).

    On Unix systems, uses fcntl for file locking.
    On Windows, relies on OS-level file locking (no fcntl needed).

    Args:
        file_path: Path to file to lock
        mode: File open mode

    Yields:
        File object with lock acquired
    """
    f = open(file_path, mode)
    try:
        # Try to acquire exclusive lock on Unix systems
        if HAS_FCNTL:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                # Lock acquisition failed, but continue anyway
                pass
        # On Windows, no explicit locking needed - OS handles it
        yield f
    finally:
        # Release lock on Unix systems
        if HAS_FCNTL:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except (IOError, OSError):
                pass
        f.close()


def read_prospects(vertical_id: str) -> pd.DataFrame:
    """
    Read prospects CSV file for a vertical.

    Args:
        vertical_id: The vertical identifier

    Returns:
        pd.DataFrame: DataFrame with prospect data, or empty DataFrame if file doesn't exist
    """
    csv_path = get_vertical_csv_path(vertical_id)

    if not os.path.exists(csv_path):
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    try:
        df = pd.read_csv(csv_path)

        # Handle empty file
        if df.empty:
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

        return df

    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    except Exception as e:
        raise IOError(f"Error reading prospects CSV for {vertical_id}: {str(e)}")


def write_prospects(vertical_id: str, df: pd.DataFrame) -> bool:
    """
    Write prospects DataFrame to CSV file atomically.

    Args:
        vertical_id: The vertical identifier
        df: DataFrame to write

    Returns:
        bool: True if successful, False otherwise
    """
    csv_path = get_vertical_csv_path(vertical_id)

    # Validate schema
    is_valid, error = validate_prospect_csv(df)
    if not is_valid:
        raise ValueError(f"Invalid prospect data: {error}")

    try:
        # Write to temporary file first (atomic operation)
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', dir=os.path.dirname(csv_path))
        os.close(temp_fd)

        # Write data to temp file
        df.to_csv(temp_path, index=False)

        # Atomic rename (replace original file)
        shutil.move(temp_path, csv_path)

        return True

    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise IOError(f"Error writing prospects CSV for {vertical_id}: {str(e)}")


def append_prospects(vertical_id: str, new_df: pd.DataFrame) -> int:
    """
    Append new prospects to existing CSV, with deduplication by email.

    Args:
        vertical_id: The vertical identifier
        new_df: DataFrame with new prospects to add

    Returns:
        int: Number of new prospects added
    """
    # Validate new data
    is_valid, error = validate_prospect_csv(new_df)
    if not is_valid:
        raise ValueError(f"Invalid prospect data: {error}")

    # Read existing prospects
    existing_df = read_prospects(vertical_id)

    # Combine and deduplicate
    if existing_df.empty:
        combined_df = new_df
    else:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    # Count before deduplication
    count_before = len(combined_df)

    # Deduplicate by email
    combined_df = deduplicate_prospects(combined_df)

    # Count after deduplication
    count_after = len(combined_df)
    count_added = count_after - len(existing_df)

    # Write back to file
    write_prospects(vertical_id, combined_df)

    return count_added


def deduplicate_prospects(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate prospects by email address.

    Args:
        df: DataFrame with prospect data

    Returns:
        pd.DataFrame: DataFrame with duplicates removed
    """
    if df.empty or 'email' not in df.columns:
        return df

    # Remove duplicates, keeping first occurrence
    # Convert emails to lowercase for comparison
    df['email_lower'] = df['email'].str.lower().str.strip()
    df = df.drop_duplicates(subset=['email_lower'], keep='first')
    df = df.drop(columns=['email_lower'])

    return df.reset_index(drop=True)


def validate_prospect_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that a DataFrame has the correct schema for prospects.

    Args:
        df: DataFrame to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    return validate_prospect_csv(df)


def get_prospect_count(vertical_id: str) -> int:
    """
    Get the total number of prospects for a vertical.

    Args:
        vertical_id: The vertical identifier

    Returns:
        int: Number of prospects
    """
    df = read_prospects(vertical_id)
    return len(df)


def get_prospect_stats(vertical_id: str, sent_df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Get statistics about prospects for a vertical.

    Args:
        vertical_id: The vertical identifier
        sent_df: Optional DataFrame from sent_tracker (to avoid reading multiple times)

    Returns:
        Dict: Statistics including total, not_contacted, initial_sent, followup_sent, etc.
    """
    df = read_prospects(vertical_id)
    total = len(df)

    stats = {
        'total': total,
        'not_contacted': 0,
        'initial_sent': 0,
        'followup_sent': 0,
        'responded': 0
    }

    if total == 0:
        return stats

    # If sent tracker provided, calculate stats
    if sent_df is not None and not sent_df.empty:
        # Filter for this vertical
        vertical_sent = sent_df[sent_df['vertical'] == vertical_id]

        # Get unique emails that received initial
        initial_emails = set(
            vertical_sent[vertical_sent['message_type'] == 'initial']['email'].unique()
        )
        stats['initial_sent'] = len(initial_emails)

        # Get unique emails that received followup
        followup_emails = set(
            vertical_sent[vertical_sent['message_type'] == 'followup']['email'].unique()
        )
        stats['followup_sent'] = len(followup_emails)

        # Calculate not contacted
        all_contacted_emails = initial_emails.union(followup_emails)
        stats['not_contacted'] = total - len(all_contacted_emails)
    else:
        stats['not_contacted'] = total

    return stats


def export_prospects_to_csv(vertical_id: str, output_path: str) -> bool:
    """
    Export prospects to a specified CSV file path.

    Args:
        vertical_id: The vertical identifier
        output_path: Path where to save the CSV

    Returns:
        bool: True if successful
    """
    df = read_prospects(vertical_id)

    try:
        df.to_csv(output_path, index=False)
        return True
    except Exception as e:
        raise IOError(f"Error exporting prospects: {str(e)}")


def import_prospects_from_csv(vertical_id: str, input_path: str, append: bool = True) -> int:
    """
    Import prospects from a CSV file.

    Args:
        vertical_id: The vertical identifier
        input_path: Path to CSV file to import
        append: If True, append to existing prospects; if False, replace

    Returns:
        int: Number of prospects added
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Import file not found: {input_path}")

    try:
        new_df = pd.read_csv(input_path)

        if append:
            return append_prospects(vertical_id, new_df)
        else:
            is_valid, error = validate_prospect_csv(new_df)
            if not is_valid:
                raise ValueError(f"Invalid prospect data: {error}")

            new_df = deduplicate_prospects(new_df)
            write_prospects(vertical_id, new_df)
            return len(new_df)

    except Exception as e:
        raise IOError(f"Error importing prospects: {str(e)}")


def create_vertical_csv(vertical_id: str) -> bool:
    """
    Create an empty CSV file for a new vertical with the correct schema.

    Args:
        vertical_id: The vertical identifier

    Returns:
        bool: True if successful
    """
    csv_path = get_vertical_csv_path(vertical_id)

    # Create directory if it doesn't exist
    csv_dir = os.path.dirname(csv_path)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir, exist_ok=True)

    # Create empty DataFrame with correct columns
    empty_df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    try:
        empty_df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        raise IOError(f"Error creating CSV file for {vertical_id}: {str(e)}")
