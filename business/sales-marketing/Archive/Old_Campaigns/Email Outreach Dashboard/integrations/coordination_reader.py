"""
Coordination JSON file reader and writer.
Manages coordination status for email campaigns.
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.windows_paths import get_coordination_path


def read_coordination() -> Dict:
    """
    Read and parse coordination.json file.

    Returns:
        Dict: Coordination data, or default structure if file doesn't exist
    """
    coord_path = get_coordination_path()

    # Default structure
    default_structure = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'last_updated': datetime.now().isoformat(),
        'initial': {
            'allocated': 0,
            'sent': 0,
            'status': 'idle'
        },
        'followup': {
            'allocated': 0,
            'sent': 0,
            'status': 'idle'
        }
    }

    if not os.path.exists(coord_path):
        return default_structure

    try:
        with open(coord_path, 'r') as f:
            data = json.load(f)

        # Ensure required fields exist
        if 'initial' not in data:
            data['initial'] = default_structure['initial']
        if 'followup' not in data:
            data['followup'] = default_structure['followup']

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in coordination file: {str(e)}")
    except Exception as e:
        raise IOError(f"Error reading coordination file: {str(e)}")


def get_allocation_status() -> Dict:
    """
    Get detailed allocation status with calculated fields.
    Uses actual sent counts from sent_tracker.csv for accuracy.

    Returns:
        Dict: Comprehensive allocation status
    """
    coord = read_coordination()

    initial = coord.get('initial', {})
    followup = coord.get('followup', {})

    initial_allocated = initial.get('allocated', 0)
    followup_allocated = followup.get('allocated', 0)

    # Get ACTUAL sent counts from sent_tracker.csv (more accurate than coordination.json)
    try:
        from .tracker_reader import read_sent_tracker
        import pandas as pd

        sent_df = read_sent_tracker()
        today = datetime.now().date()

        if not sent_df.empty and 'timestamp' in sent_df.columns and 'message_type' in sent_df.columns:
            sent_df['date'] = pd.to_datetime(sent_df['timestamp']).dt.date
            today_df = sent_df[sent_df['date'] == today]

            # Count by message type
            initial_sent = len(today_df[today_df['message_type'] == 'initial'])
            followup_sent = len(today_df[today_df['message_type'] == 'followup'])
        else:
            # Fallback to coordination.json if tracker unavailable
            initial_sent = initial.get('sent', 0)
            followup_sent = followup.get('sent', 0)
    except Exception:
        # Fallback to coordination.json on any error
        initial_sent = initial.get('sent', 0)
        followup_sent = followup.get('sent', 0)

    initial_remaining = max(0, initial_allocated - initial_sent)
    followup_remaining = max(0, followup_allocated - followup_sent)

    total_capacity = initial_allocated + followup_allocated
    total_sent = initial_sent + followup_sent
    total_remaining = initial_remaining + followup_remaining

    return {
        'date': coord.get('date', datetime.now().strftime('%Y-%m-%d')),
        'last_updated': coord.get('last_updated', ''),
        'initial': {
            'allocated': initial_allocated,
            'sent': initial_sent,
            'remaining': initial_remaining,
            'status': initial.get('status', 'idle')
        },
        'followup': {
            'allocated': followup_allocated,
            'sent': followup_sent,
            'remaining': followup_remaining,
            'status': followup.get('status', 'idle')
        },
        'total_capacity': total_capacity,
        'total_sent': total_sent,
        'total_remaining': total_remaining
    }


def is_capacity_available() -> bool:
    """
    Check if there is remaining capacity for sending emails.

    Returns:
        bool: True if capacity available, False otherwise
    """
    status = get_allocation_status()
    return status['total_remaining'] > 0


def get_daily_summary() -> str:
    """
    Get a human-readable summary of today's coordination status.

    Returns:
        str: Formatted summary string
    """
    status = get_allocation_status()

    summary_lines = [
        f"Date: {status['date']}",
        f"Total Capacity: {status['total_capacity']} emails",
        f"Total Sent: {status['total_sent']} emails",
        f"Remaining: {status['total_remaining']} emails",
        "",
        "Initial Outreach:",
        f"  Allocated: {status['initial']['allocated']}",
        f"  Sent: {status['initial']['sent']}",
        f"  Remaining: {status['initial']['remaining']}",
        f"  Status: {status['initial']['status']}",
        "",
        "Follow-up:",
        f"  Allocated: {status['followup']['allocated']}",
        f"  Sent: {status['followup']['sent']}",
        f"  Remaining: {status['followup']['remaining']}",
        f"  Status: {status['followup']['status']}"
    ]

    return "\n".join(summary_lines)


def update_coordination(
    initial_allocated: Optional[int] = None,
    initial_sent: Optional[int] = None,
    initial_status: Optional[str] = None,
    followup_allocated: Optional[int] = None,
    followup_sent: Optional[int] = None,
    followup_status: Optional[str] = None,
    update_date: bool = False
) -> bool:
    """
    Update coordination.json file atomically.

    Args:
        initial_allocated: New allocated count for initial (or None to keep current)
        initial_sent: New sent count for initial (or None to keep current)
        initial_status: New status for initial (or None to keep current)
        followup_allocated: New allocated count for followup (or None to keep current)
        followup_sent: New sent count for followup (or None to keep current)
        followup_status: New status for followup (or None to keep current)
        update_date: If True, update the date to today

    Returns:
        bool: True if successful
    """
    coord_path = get_coordination_path()

    # Read current data
    current_data = read_coordination()

    # Update fields if provided
    if initial_allocated is not None:
        current_data['initial']['allocated'] = initial_allocated
    if initial_sent is not None:
        current_data['initial']['sent'] = initial_sent
    if initial_status is not None:
        current_data['initial']['status'] = initial_status

    if followup_allocated is not None:
        current_data['followup']['allocated'] = followup_allocated
    if followup_sent is not None:
        current_data['followup']['sent'] = followup_sent
    if followup_status is not None:
        current_data['followup']['status'] = followup_status

    # Update timestamp
    current_data['last_updated'] = datetime.now().isoformat()

    if update_date:
        current_data['date'] = datetime.now().strftime('%Y-%m-%d')

    # Write atomically (temp file then rename)
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(coord_path), exist_ok=True)

        # Write to temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.json', dir=os.path.dirname(coord_path))
        os.close(temp_fd)

        with open(temp_path, 'w') as f:
            json.dump(current_data, f, indent=2)

        # Atomic rename
        shutil.move(temp_path, coord_path)

        return True

    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise IOError(f"Error updating coordination file: {str(e)}")


def reset_daily_coordination(initial_allocated: int = 225, followup_allocated: int = 225) -> bool:
    """
    Reset coordination for a new day.

    Args:
        initial_allocated: Allocated capacity for initial emails
        followup_allocated: Allocated capacity for followup emails

    Returns:
        bool: True if successful
    """
    return update_coordination(
        initial_allocated=initial_allocated,
        initial_sent=0,
        initial_status='idle',
        followup_allocated=followup_allocated,
        followup_sent=0,
        followup_status='idle',
        update_date=True
    )


def pause_campaign(campaign_type: str) -> bool:
    """
    Pause a campaign (initial or followup).

    Args:
        campaign_type: 'initial' or 'followup'

    Returns:
        bool: True if successful
    """
    if campaign_type == 'initial':
        return update_coordination(initial_status='paused')
    elif campaign_type == 'followup':
        return update_coordination(followup_status='paused')
    else:
        raise ValueError(f"Invalid campaign type: {campaign_type}")


def resume_campaign(campaign_type: str) -> bool:
    """
    Resume a paused campaign.

    Args:
        campaign_type: 'initial' or 'followup'

    Returns:
        bool: True if successful
    """
    if campaign_type == 'initial':
        return update_coordination(initial_status='running')
    elif campaign_type == 'followup':
        return update_coordination(followup_status='running')
    else:
        raise ValueError(f"Invalid campaign type: {campaign_type}")


def get_capacity_allocation() -> Dict:
    """
    Get the capacity allocation split between initial and followup.

    Returns:
        Dict: Allocation details
    """
    status = get_allocation_status()

    return {
        'initial_allocated': status['initial']['allocated'],
        'followup_allocated': status['followup']['allocated'],
        'total_capacity': status['total_capacity'],
        'split_ratio': {
            'initial': status['initial']['allocated'] / status['total_capacity'] if status['total_capacity'] > 0 else 0.5,
            'followup': status['followup']['allocated'] / status['total_capacity'] if status['total_capacity'] > 0 else 0.5
        }
    }


def get_vertical_status_breakdown() -> list:
    """
    Get campaign status breakdown by vertical.

    Returns:
        List[Dict]: Status for each vertical/campaign combination
    """
    try:
        from .tracker_reader import read_sent_tracker
        from .csv_handler import get_prospect_stats
        import pandas as pd
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database import models

        sent_df = read_sent_tracker()
        today = datetime.now().date()
        verticals = models.get_verticals(active_only=True)

        breakdown = []

        if not verticals:
            return breakdown

        for vertical in verticals:
            vertical_id = vertical['vertical_id']

            # Get prospect availability
            try:
                stats = get_prospect_stats(vertical_id)
                initial_available = stats.get('not_contacted', 0)
                followup_available = stats.get('followup_ready', 0)
            except:
                initial_available = 0
                followup_available = 0

            # Count sent by type for today
            initial_sent = 0
            followup_sent = 0

            if not sent_df.empty and 'timestamp' in sent_df.columns:
                sent_df['date'] = pd.to_datetime(sent_df['timestamp']).dt.date
                vertical_today = sent_df[(sent_df['date'] == today) & (sent_df['vertical'] == vertical_id)]

                if 'message_type' in sent_df.columns:
                    initial_sent = len(vertical_today[vertical_today['message_type'] == 'initial'])
                    followup_sent = len(vertical_today[vertical_today['message_type'] == 'followup'])

            # Add initial row
            breakdown.append({
                'vertical': vertical['display_name'],
                'vertical_id': vertical_id,
                'campaign_type': 'Initial',
                'sent': initial_sent,
                'available': initial_available,
                'status': 'ACTIVE' if initial_sent > 0 else 'IDLE'
            })

            # Add followup row
            breakdown.append({
                'vertical': vertical['display_name'],
                'vertical_id': vertical_id,
                'campaign_type': 'Followup',
                'sent': followup_sent,
                'available': followup_available,
                'status': 'ACTIVE' if followup_sent > 0 else 'IDLE'
            })

        return breakdown

    except Exception as e:
        print(f"Error getting vertical breakdown: {e}")
        return []
