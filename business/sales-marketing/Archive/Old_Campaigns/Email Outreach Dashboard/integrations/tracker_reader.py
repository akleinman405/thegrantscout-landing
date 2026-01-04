"""
Tracker CSV file reader for sent emails and responses.
Provides metrics and analytics from tracker files.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import time

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.windows_paths import get_sent_tracker_path, get_response_tracker_path


# Simple cache with time-based expiration (60 seconds)
_cache = {}
_cache_timeout = 60  # seconds


def _get_cached(key: str, fetch_func):
    """
    Get data from cache or fetch and cache it.

    Args:
        key: Cache key
        fetch_func: Function to call if cache miss

    Returns:
        Cached or freshly fetched data
    """
    current_time = time.time()

    if key in _cache:
        data, timestamp = _cache[key]
        if current_time - timestamp < _cache_timeout:
            return data

    # Cache miss or expired, fetch fresh data
    data = fetch_func()
    _cache[key] = (data, current_time)
    return data


def read_sent_tracker() -> pd.DataFrame:
    """
    Read the sent emails tracker CSV.

    Returns:
        pd.DataFrame: DataFrame with sent email data
    """
    def _fetch():
        tracker_path = get_sent_tracker_path()

        if not os.path.exists(tracker_path):
            return pd.DataFrame(columns=[
                'timestamp', 'email', 'vertical', 'message_type',
                'subject_line', 'status', 'error_message'
            ])

        try:
            df = pd.read_csv(tracker_path)

            if df.empty:
                return df

            # Parse timestamp column
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

                # Add date column (without time)
                df['date'] = df['timestamp'].dt.date

            return df

        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=[
                'timestamp', 'email', 'vertical', 'message_type',
                'subject_line', 'status', 'error_message'
            ])
        except Exception as e:
            raise IOError(f"Error reading sent tracker: {str(e)}")

    return _get_cached('sent_tracker', _fetch)


def read_response_tracker() -> pd.DataFrame:
    """
    Read the response tracker CSV.

    Returns:
        pd.DataFrame: DataFrame with response data
    """
    def _fetch():
        tracker_path = get_response_tracker_path()

        if not os.path.exists(tracker_path):
            return pd.DataFrame(columns=[
                'timestamp', 'email', 'vertical', 'response_status', 'response_text'
            ])

        try:
            df = pd.read_csv(tracker_path)

            if df.empty:
                return df

            # Parse timestamp column
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df['date'] = df['timestamp'].dt.date

            return df

        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=[
                'timestamp', 'email', 'vertical', 'response_status', 'response_text'
            ])
        except Exception as e:
            raise IOError(f"Error reading response tracker: {str(e)}")

    return _get_cached('response_tracker', _fetch)


def get_sent_count(
    vertical: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> int:
    """
    Get count of sent emails with optional filters.

    Args:
        vertical: Filter by vertical ID
        date_from: Start date filter
        date_to: End date filter

    Returns:
        int: Count of sent emails
    """
    df = read_sent_tracker()

    if df.empty:
        return 0

    # Apply filters
    if vertical:
        df = df[df['vertical'] == vertical]

    if date_from:
        df = df[df['timestamp'] >= date_from]

    if date_to:
        df = df[df['timestamp'] <= date_to]

    return len(df)


def get_sent_by_date(vertical: Optional[str] = None) -> pd.DataFrame:
    """
    Get sent emails grouped by date.

    Args:
        vertical: Optional vertical filter

    Returns:
        pd.DataFrame: DataFrame with columns: date, count
    """
    df = read_sent_tracker()

    if df.empty:
        return pd.DataFrame(columns=['date', 'count'])

    if vertical:
        df = df[df['vertical'] == vertical]

    if 'date' not in df.columns:
        return pd.DataFrame(columns=['date', 'count'])

    # Group by date
    daily_counts = df.groupby('date').size().reset_index(name='count')
    daily_counts = daily_counts.sort_values('date')

    return daily_counts


def get_sent_by_vertical() -> Dict[str, int]:
    """
    Get sent email counts grouped by vertical.

    Returns:
        Dict[str, int]: Dictionary mapping vertical_id to count
    """
    df = read_sent_tracker()

    if df.empty or 'vertical' not in df.columns:
        return {}

    counts = df['vertical'].value_counts().to_dict()
    return counts


def calculate_response_rate(vertical: Optional[str] = None) -> float:
    """
    Calculate response rate (responses / sent).

    Args:
        vertical: Optional vertical filter

    Returns:
        float: Response rate as decimal (e.g., 0.125 for 12.5%)
    """
    sent_df = read_sent_tracker()
    response_df = read_response_tracker()

    if sent_df.empty:
        return 0.0

    # Filter by vertical if specified
    if vertical:
        sent_df = sent_df[sent_df['vertical'] == vertical]
        if not response_df.empty and 'vertical' in response_df.columns:
            response_df = response_df[response_df['vertical'] == vertical]

    total_sent = len(sent_df)

    if total_sent == 0:
        return 0.0

    # Count responses (excluding PENDING status)
    if response_df.empty:
        return 0.0

    # Check for actual responses (not PENDING)
    if 'replied' in response_df.columns:
        # Filter out PENDING responses
        responses = response_df[response_df['replied'] != 'PENDING']
        response_count = len(responses)
    elif 'response_status' in response_df.columns:
        responses = response_df[response_df['response_status'] != 'PENDING']
        response_count = len(responses)
    else:
        # No status column, count all rows (fallback)
        response_count = len(response_df)

    return response_count / total_sent if total_sent > 0 else 0.0


def get_daily_metrics(date: Optional[datetime] = None) -> Dict:
    """
    Get metrics for a specific date or today.

    Args:
        date: Date to get metrics for (defaults to today)

    Returns:
        Dict: Metrics including sent_today, sent_this_week, response_rate, etc.
    """
    if date is None:
        date = datetime.now()

    today = date.date()
    week_ago = (date - timedelta(days=7)).date()
    month_ago = (date - timedelta(days=30)).date()

    sent_df = read_sent_tracker()

    if sent_df.empty or 'date' not in sent_df.columns:
        return {
            'sent_today': 0,
            'sent_this_week': 0,
            'sent_this_month': 0,
            'response_rate': 0.0,
            'error_rate': 0.0
        }

    # Convert date column to proper date objects if needed
    sent_df['date'] = pd.to_datetime(sent_df['date']).dt.date

    # Count sent emails
    sent_today = len(sent_df[sent_df['date'] == today])
    sent_this_week = len(sent_df[sent_df['date'] >= week_ago])
    sent_this_month = len(sent_df[sent_df['date'] >= month_ago])

    # Calculate error rate
    if 'status' in sent_df.columns:
        total = len(sent_df)
        errors = len(sent_df[sent_df['status'] != 'SUCCESS'])
        error_rate = errors / total if total > 0 else 0.0
    else:
        error_rate = 0.0

    return {
        'sent_today': sent_today,
        'sent_this_week': sent_this_week,
        'sent_this_month': sent_this_month,
        'response_rate': calculate_response_rate(),
        'error_rate': error_rate
    }


def get_vertical_breakdown() -> List[Dict]:
    """
    Get breakdown of metrics by vertical.

    Returns:
        List[Dict]: List of dictionaries with vertical metrics
    """
    sent_df = read_sent_tracker()

    if sent_df.empty or 'vertical' not in sent_df.columns:
        return []

    verticals = sent_df['vertical'].unique()
    today = datetime.now().date()

    breakdown = []
    for vertical in verticals:
        vertical_df = sent_df[sent_df['vertical'] == vertical].copy()

        # Count total sent
        sent_total = len(vertical_df)

        # Count sent today
        if 'date' in vertical_df.columns:
            vertical_df['date'] = pd.to_datetime(vertical_df['date']).dt.date
            sent_today = len(vertical_df[vertical_df['date'] == today])
        else:
            sent_today = 0

        # Calculate response rate for this vertical
        response_rate = calculate_response_rate(vertical=vertical)

        breakdown.append({
            'vertical': vertical,
            'sent_total': sent_total,
            'sent_today': sent_today,
            'response_rate': response_rate
        })

    return breakdown


def get_account_daily_sent(account_email: str, date: Optional[datetime] = None) -> int:
    """
    Get number of emails sent by a specific account today.

    Args:
        account_email: Email address of the sending account
        date: Date to check (defaults to today)

    Returns:
        int: Number of emails sent
    """
    # Note: The current sent_tracker doesn't track which account sent the email
    # This is a placeholder for future enhancement
    # For now, we'll count all sent emails for the day
    if date is None:
        date = datetime.now()

    today = date.date()
    sent_df = read_sent_tracker()

    if sent_df.empty or 'date' not in sent_df.columns:
        return 0

    sent_df['date'] = pd.to_datetime(sent_df['date']).dt.date
    return len(sent_df[sent_df['date'] == today])


def get_metrics(vertical_id: Optional[str] = None, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict:
    """
    Get comprehensive metrics with optional filters.

    Args:
        vertical_id: Optional vertical filter
        date_range: Optional tuple of (start_date, end_date)

    Returns:
        Dict: Comprehensive metrics
    """
    sent_df = read_sent_tracker()
    response_df = read_response_tracker()

    # Apply filters
    if vertical_id and not sent_df.empty:
        sent_df = sent_df[sent_df['vertical'] == vertical_id]
        if not response_df.empty and 'vertical' in response_df.columns:
            response_df = response_df[response_df['vertical'] == vertical_id]

    if date_range and not sent_df.empty and 'timestamp' in sent_df.columns:
        start_date, end_date = date_range
        sent_df = sent_df[(sent_df['timestamp'] >= start_date) & (sent_df['timestamp'] <= end_date)]

    # Calculate metrics
    total_sent = len(sent_df) if not sent_df.empty else 0
    total_responses = len(response_df) if not response_df.empty else 0

    # Count by message type
    initial_count = 0
    followup_count = 0
    if not sent_df.empty and 'message_type' in sent_df.columns:
        initial_count = len(sent_df[sent_df['message_type'] == 'initial'])
        followup_count = len(sent_df[sent_df['message_type'] == 'followup'])

    # Calculate response rate
    response_rate = total_responses / total_sent if total_sent > 0 else 0.0

    return {
        'total_sent': total_sent,
        'initial_sent': initial_count,
        'followup_sent': followup_count,
        'total_responses': total_responses,
        'response_rate': response_rate,
        'vertical': vertical_id,
        'date_range': date_range
    }


def clear_cache():
    """Clear the internal cache (useful for testing or forcing refresh)."""
    global _cache
    _cache = {}
