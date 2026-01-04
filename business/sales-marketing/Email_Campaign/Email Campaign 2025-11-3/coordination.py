"""
Coordination system for managing email capacity allocation between initial and followup scripts.

Rules:
- Followups get up to HALF (225) of daily 450 capacity
- Initial gets the rest
- Both scripts can run simultaneously
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple
import pytz
import pandas as pd

# Import config for paths and settings
import config

COORDINATION_FILE = os.path.join(config.BASE_DIR, "coordination.json")
MAX_FOLLOWUP_CAPACITY = config.TOTAL_DAILY_LIMIT // 2  # Half of daily limit


def get_current_time_est() -> datetime:
    """Get current time in EST"""
    return datetime.now(pytz.timezone(config.TIMEZONE))


def load_coordination() -> Dict:
    """Load coordination file or create new one if doesn't exist or is stale"""
    today = get_current_time_est().strftime('%Y-%m-%d')
    
    if not os.path.exists(COORDINATION_FILE):
        return create_new_coordination(today)
    
    try:
        with open(COORDINATION_FILE, 'r') as f:
            coord = json.load(f)
        
        # If coordination is from different day, create new one
        if coord.get('date') != today:
            return create_new_coordination(today)
        
        return coord
    except Exception as e:
        print(f"⚠️  Error loading coordination file: {e}")
        return create_new_coordination(today)


def create_new_coordination(date: str) -> Dict:
    """Create new coordination structure for the day"""
    coord = {
        'date': date,
        'last_updated': get_current_time_est().isoformat(),
        'initial': {
            'needs': 0,
            'allocated': 0,
            'sent': 0,
            'status': 'idle'
        },
        'followup': {
            'needs': 0,
            'allocated': 0,
            'sent': 0,
            'status': 'idle'
        }
    }
    save_coordination(coord)
    return coord


def save_coordination(coord: Dict):
    """Save coordination file"""
    coord['last_updated'] = get_current_time_est().isoformat()
    
    try:
        with open(COORDINATION_FILE, 'w') as f:
            json.dump(coord, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving coordination file: {e}")


def calculate_allocation(initial_needs: int, followup_needs: int) -> Tuple[int, int]:
    """
    Calculate fair allocation between initial and followup.

    Rules:
    - If followup needs < 225: followup gets what it needs, initial fills the rest
    - If both need > 225: each gets 225 (50/50 split)
    - Total always <= 450

    Args:
        initial_needs: Number of initial emails ready to send
        followup_needs: Number of followups ready to send

    Returns:
        (initial_allocation, followup_allocation)
    """
    # Cap followup at half of daily capacity
    followup_allocation = min(followup_needs, MAX_FOLLOWUP_CAPACITY)

    # Initial gets the rest (up to total limit)
    initial_allocation = min(initial_needs, config.TOTAL_DAILY_LIMIT - followup_allocation)

    return initial_allocation, followup_allocation


def report_needs_and_allocate(script_type: str, needs: int) -> int:
    """
    Report how many emails this script needs to send and get allocation.
    Triggers reallocation if this is new information.

    Args:
        script_type: 'initial' or 'followup'
        needs: How many emails this script wants to send

    Returns:
        Allocated capacity for this script
    """
    coord = load_coordination()

    # Update needs for this script
    coord[script_type]['needs'] = needs

    # Get the other script's needs
    other_type = 'followup' if script_type == 'initial' else 'initial'
    other_needs = coord[other_type]['needs']

    # Calculate allocation based on both needs
    initial_alloc, followup_alloc = calculate_allocation(
        coord['initial']['needs'],
        coord['followup']['needs']
    )

    # Update allocations
    coord['initial']['allocated'] = initial_alloc
    coord['followup']['allocated'] = followup_alloc
    coord[script_type]['status'] = 'running'

    save_coordination(coord)

    return coord[script_type]['allocated']


def update_sent_count(script_type: str, sent_count: int):
    """
    Update how many emails this script has sent.
    
    Args:
        script_type: 'initial' or 'followup'
        sent_count: Total sent by this script today
    """
    coord = load_coordination()
    coord[script_type]['sent'] = sent_count
    save_coordination(coord)


def get_remaining_capacity(script_type: str) -> int:
    """
    Get remaining capacity for this script.
    
    Args:
        script_type: 'initial' or 'followup'
    
    Returns:
        How many more emails this script can send today
    """
    coord = load_coordination()
    allocated = coord[script_type]['allocated']
    sent = coord[script_type]['sent']
    return max(0, allocated - sent)


def get_status_summary() -> Dict:
    """
    Get comprehensive status summary showing needs, allocations, and remaining capacity.
    This is the central status location both scripts can check.

    Returns:
        Dictionary with complete status information
    """
    coord = load_coordination()

    initial_remaining = max(0, coord['initial']['allocated'] - coord['initial']['sent'])
    followup_remaining = max(0, coord['followup']['allocated'] - coord['followup']['sent'])

    return {
        'date': coord['date'],
        'last_updated': coord.get('last_updated', ''),
        'initial': {
            'needs': coord['initial']['needs'],
            'allocated': coord['initial']['allocated'],
            'sent': coord['initial']['sent'],
            'remaining': initial_remaining,
            'status': coord['initial']['status']
        },
        'followup': {
            'needs': coord['followup']['needs'],
            'allocated': coord['followup']['allocated'],
            'sent': coord['followup']['sent'],
            'remaining': followup_remaining,
            'status': coord['followup']['status']
        },
        'total': {
            'needs': coord['initial']['needs'] + coord['followup']['needs'],
            'allocated': coord['initial']['allocated'] + coord['followup']['allocated'],
            'sent': coord['initial']['sent'] + coord['followup']['sent'],
            'remaining': initial_remaining + followup_remaining
        }
    }


def mark_script_running(script_type: str):
    """Mark script as running"""
    coord = load_coordination()
    coord[script_type]['status'] = 'running'
    save_coordination(coord)


def mark_script_stopped(script_type: str):
    """Mark script as stopped"""
    coord = load_coordination()
    coord[script_type]['status'] = 'stopped'
    save_coordination(coord)


def get_allocation_summary() -> Dict:
    """Get current allocation summary for display"""
    coord = load_coordination()
    return {
        'date': coord['date'],
        'initial': {
            'allocated': coord['initial']['allocated'],
            'sent': coord['initial']['sent'],
            'remaining': max(0, coord['initial']['allocated'] - coord['initial']['sent']),
            'status': coord['initial']['status']
        },
        'followup': {
            'allocated': coord['followup']['allocated'],
            'sent': coord['followup']['sent'],
            'remaining': max(0, coord['followup']['allocated'] - coord['followup']['sent']),
            'status': coord['followup']['status']
        },
        'total_allocated': coord['initial']['allocated'] + coord['followup']['allocated'],
        'total_sent': coord['initial']['sent'] + coord['followup']['sent']
    }




def get_vertical_sent_counts(message_type='initial'):
    """Get count of successfully sent emails by vertical"""
    if not os.path.exists(config.SENT_TRACKER):
        return {}
    
    try:
        import pandas as pd
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return {}
        
        # Filter to successful sends of specified type
        filtered = df[(df['status'] == 'SUCCESS') & (df['message_type'] == message_type)]
        
        # Count by vertical
        counts = filtered.groupby('vertical').size().to_dict()
        return counts
    except Exception as e:
        return {}


def get_vertical_sent_last_24h(message_type='initial'):
    """Get count of emails sent in last 24 hours by vertical"""
    if not os.path.exists(config.SENT_TRACKER):
        return {}
    
    try:
        import pandas as pd
        from datetime import datetime, timedelta
        
        df = pd.read_csv(config.SENT_TRACKER)
        if df.empty:
            return {}
        
        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Get cutoff (24 hours ago)
        cutoff = get_current_time_est() - timedelta(hours=24)
        if cutoff.tzinfo is None:
            cutoff = pytz.timezone(config.TIMEZONE).localize(cutoff)
        cutoff_utc = cutoff.astimezone(pytz.UTC)
        
        # Filter
        filtered = df[
            (df['status'] == 'SUCCESS') & 
            (df['message_type'] == message_type) &
            (df['timestamp'] >= cutoff_utc)
        ]
        
        # Count by vertical
        counts = filtered.groupby('vertical').size().to_dict()
        return counts
    except Exception as e:
        return {}


def display_allocation_summary():
    """Display enhanced allocation summary with vertical breakdowns"""
    summary = get_status_summary()
    
    # Get vertical statistics
    initial_sent_alltime = get_vertical_sent_counts('initial')
    initial_sent_24h = get_vertical_sent_last_24h('initial')
    followup_sent_alltime = get_vertical_sent_counts('followup')
    followup_sent_24h = get_vertical_sent_last_24h('followup')

    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  COORDINATION STATUS - CENTRAL VIEW                        ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  Date: {summary['date']:<49} ║")
    print("║                                                            ║")
    
    # Initial Outreach Section
    print("║  Initial Outreach:                                         ║")
    print(f"║    Needs:     {summary['initial']['needs']:<44} ║")
    print(f"║    Allocated: {summary['initial']['allocated']:<44} ║")
    print(f"║    Sent:      {summary['initial']['sent']:<44} ║")
    print(f"║    Remaining: {summary['initial']['remaining']:<44} ║")
    print(f"║    Status:    {summary['initial']['status']:<44} ║")
    
    # Show vertical breakdown for initial
    if initial_sent_alltime or initial_sent_24h:
        print("║                                                            ║")
        print("║    By Vertical (Sent All-Time / Last 24h):                ║")
        for vertical in config.ACTIVE_VERTICALS:
            if vertical in initial_sent_alltime or vertical in initial_sent_24h:
                name = config.VERTICALS[vertical]['name'][:18]
                alltime = initial_sent_alltime.get(vertical, 0)
                last_24h = initial_sent_24h.get(vertical, 0)
                print(f"║      {name:<18} {alltime:>5} / {last_24h:<5}                     ║")
    
    print("║                                                            ║")
    
    # Follow-up Section
    print("║  Follow-up:                                                ║")
    print(f"║    Needs:     {summary['followup']['needs']:<44} ║")
    print(f"║    Allocated: {summary['followup']['allocated']:<44} ║")
    print(f"║    Sent:      {summary['followup']['sent']:<44} ║")
    print(f"║    Remaining: {summary['followup']['remaining']:<44} ║")
    print(f"║    Status:    {summary['followup']['status']:<44} ║")
    
    # Show vertical breakdown for followup
    if followup_sent_alltime or followup_sent_24h:
        print("║                                                            ║")
        print("║    By Vertical (Sent All-Time / Last 24h):                ║")
        for vertical in config.ACTIVE_VERTICALS:
            if vertical in followup_sent_alltime or vertical in followup_sent_24h:
                name = config.VERTICALS[vertical]['name'][:18]
                alltime = followup_sent_alltime.get(vertical, 0)
                last_24h = followup_sent_24h.get(vertical, 0)
                print(f"║      {name:<18} {alltime:>5} / {last_24h:<5}                     ║")
    
    print("║                                                            ║")
    
    # Totals
    print(f"║  Total Needs:     {summary['total']['needs']:<40} ║")
    print(f"║  Total Allocated: {summary['total']['allocated']:<40} ║")
    print(f"║  Total Sent:      {summary['total']['sent']:<40} ║")
    print(f"║  Total Remaining: {summary['total']['remaining']:<40} ║")
    print("╚════════════════════════════════════════════════════════════╝\n")


def get_rolling_capacity_analysis(current_time: datetime, business_hours_end: datetime, daily_limit: int = None) -> Dict:
    """
    Analyze rolling 24h capacity with age-out projections.

    This function calculates not just current capacity, but also projects when
    additional capacity will become available as emails age out of the 24-hour window.

    Args:
        current_time: Current datetime (EST, timezone-aware)
        business_hours_end: End of sending window today (EST, timezone-aware)
        daily_limit: Maximum emails in any 24h period (default 300)

    Returns:
        dict with:
            - emails_in_last_24h: Count of emails sent in last 24h
            - current_capacity: Can send right now
            - capacity_by_hour: Dict mapping hour to cumulative capacity
            - total_capacity_by_eob: Total sendable by end of business
            - will_free_by_eob: Additional capacity that will free up
            - next_capacity_at: When next capacity will free (or None)
    """
    # Default to config value if not specified
    if daily_limit is None:
        daily_limit = config.TOTAL_DAILY_LIMIT

    # Check if tracker file exists
    if not os.path.exists(config.SENT_TRACKER):
        # No emails sent yet - full capacity
        return {
            'emails_in_last_24h': 0,
            'current_capacity': daily_limit,
            'capacity_by_hour': {},
            'total_capacity_by_eob': daily_limit,
            'will_free_by_eob': 0,
            'next_capacity_at': None,
            'emails_by_hour': {}
        }

    try:
        # Load sent tracker
        df = pd.read_csv(config.SENT_TRACKER)

        if df.empty:
            # No emails sent yet - full capacity
            return {
                'emails_in_last_24h': 0,
                'current_capacity': daily_limit,
                'capacity_by_hour': {},
                'total_capacity_by_eob': daily_limit,
                'will_free_by_eob': 0,
                'next_capacity_at': None,
                'emails_by_hour': {}
            }

        # Filter to successful sends only
        df = df[df['status'] == 'SUCCESS']

        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # Get cutoff time (24 hours ago)
        cutoff = current_time - timedelta(hours=24)
        if cutoff.tzinfo is None:
            cutoff = pytz.timezone(config.TIMEZONE).localize(cutoff)

        # Filter to last 24 hours
        df_last_24h = df[df['timestamp'] >= cutoff]
        emails_in_last_24h = len(df_last_24h)

        if emails_in_last_24h == 0:
            # No emails in last 24h - full capacity
            return {
                'emails_in_last_24h': 0,
                'current_capacity': daily_limit,
                'capacity_by_hour': {},
                'total_capacity_by_eob': daily_limit,
                'will_free_by_eob': 0,
                'next_capacity_at': None,
                'emails_by_hour': {}
            }

        # Group emails by hour sent (rounded down to hour)
        df_last_24h['hour_sent'] = df_last_24h['timestamp'].dt.floor('H')
        emails_by_hour = df_last_24h.groupby('hour_sent').size().to_dict()

        # Calculate age-out schedule (when each hour's emails become >24h old)
        age_out_schedule = {}
        for hour_sent, count in emails_by_hour.items():
            age_out_time = hour_sent + timedelta(hours=24)
            age_out_schedule[age_out_time] = count

        # Calculate current capacity (emails still in window)
        emails_still_in_window = sum([
            count for age_out_time, count in age_out_schedule.items()
            if age_out_time > current_time
        ])
        current_capacity = max(0, daily_limit - emails_still_in_window)

        # Project capacity hour by hour until end of business
        capacity_by_hour = {}

        # Ensure current_time and business_hours_end are timezone-aware
        if current_time.tzinfo is None:
            current_time = pytz.timezone(config.TIMEZONE).localize(current_time)
        if business_hours_end.tzinfo is None:
            business_hours_end = pytz.timezone(config.TIMEZONE).localize(business_hours_end)

        # Generate hourly timestamps from now until end of business
        current_hour = current_time.replace(minute=0, second=0, microsecond=0)
        end_hour = business_hours_end.replace(minute=0, second=0, microsecond=0)

        # Add current time as first entry
        capacity_by_hour[current_time] = current_capacity

        # Project capacity for each hour
        hour = current_hour + timedelta(hours=1)
        while hour <= end_hour:
            # Count how many will age out by this hour
            freed_by_hour = sum([
                count for age_out_time, count in age_out_schedule.items()
                if current_time < age_out_time <= hour
            ])
            capacity_by_hour[hour] = min(daily_limit, current_capacity + freed_by_hour)
            hour += timedelta(hours=1)

        # Calculate total capacity by end of business
        if capacity_by_hour:
            total_capacity_by_eob = max(capacity_by_hour.values())
        else:
            total_capacity_by_eob = current_capacity

        will_free_by_eob = total_capacity_by_eob - current_capacity

        # Find next time capacity will free up
        next_capacity_at = None
        for age_out_time in sorted(age_out_schedule.keys()):
            if age_out_time > current_time and age_out_time <= business_hours_end:
                next_capacity_at = age_out_time
                break

        return {
            'emails_in_last_24h': emails_in_last_24h,
            'current_capacity': current_capacity,
            'capacity_by_hour': capacity_by_hour,
            'total_capacity_by_eob': total_capacity_by_eob,
            'will_free_by_eob': will_free_by_eob,
            'next_capacity_at': next_capacity_at,
            'emails_by_hour': emails_by_hour
        }

    except Exception as e:
        print(f"⚠️  Error analyzing rolling capacity: {e}")
        # Fallback to simple calculation
        simple_count = 0
        if os.path.exists(config.SENT_TRACKER):
            try:
                df = pd.read_csv(config.SENT_TRACKER)
                df = df[df['status'] == 'SUCCESS']
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                cutoff = current_time - timedelta(hours=24)
                if cutoff.tzinfo is None:
                    cutoff = pytz.timezone(config.TIMEZONE).localize(cutoff)
                simple_count = len(df[df['timestamp'] >= cutoff])
            except:
                pass

        return {
            'emails_in_last_24h': simple_count,
            'current_capacity': max(0, daily_limit - simple_count),
            'capacity_by_hour': {},
            'total_capacity_by_eob': max(0, daily_limit - simple_count),
            'will_free_by_eob': 0,
            'next_capacity_at': None,
            'emails_by_hour': {}
        }


def get_steady_state_pacing() -> Dict:
    """
    Calculate steady-state pacing to consistently send 400 emails/day.

    This solves the "not sending full amount" problem by:
    1. Targeting 40 emails/hour across 10 business hours (9am-7pm EST)
    2. Using calendar-day tracking (not rolling 24h) for pacing decisions
    3. Catching up if behind schedule, staying consistent if on track

    Returns:
        dict with:
            - target_per_hour: Emails to send this hour
            - delay_seconds: Seconds between emails
            - emails_sent_today: Calendar-day count
            - target_by_now: What we should have sent by now
            - status: 'ahead', 'on_track', or 'behind'
            - can_send: True if we should send now
            - message: Human-readable status
    """
    now = get_current_time_est()

    # Business hours
    business_start = now.replace(hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0)
    business_end = now.replace(hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)

    # Check if within business hours
    is_weekday = now.weekday() < 5
    is_business_hours = business_start <= now <= business_end

    if not is_weekday or not is_business_hours:
        return {
            'target_per_hour': 0,
            'delay_seconds': 0,
            'emails_sent_today': 0,
            'target_by_now': 0,
            'status': 'outside_hours',
            'can_send': False,
            'message': 'Outside business hours (Mon-Fri 9am-7pm EST)'
        }

    # Count emails sent TODAY (calendar day, not rolling 24h)
    today_str = now.strftime('%Y-%m-%d')
    emails_sent_today = 0

    if os.path.exists(config.SENT_TRACKER):
        try:
            df = pd.read_csv(config.SENT_TRACKER)
            df = df[df['status'] == 'SUCCESS']
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

            # Convert to EST and filter to today
            df['date_est'] = df['timestamp'].dt.tz_convert(config.TIMEZONE).dt.date
            today_date = now.date()
            emails_sent_today = len(df[df['date_est'] == today_date])
        except Exception as e:
            print(f"⚠️  Error reading tracker for pacing: {e}")

    # Calculate targets
    total_business_hours = config.BUSINESS_HOURS_END - config.BUSINESS_HOURS_START  # 10 hours
    target_per_hour = config.TOTAL_DAILY_LIMIT / total_business_hours  # 40 emails/hour

    # How many hours into business day are we?
    hours_elapsed = (now - business_start).total_seconds() / 3600
    hours_remaining = max(0.5, (business_end - now).total_seconds() / 3600)  # Min 30 min

    # What should we have sent by now?
    target_by_now = int(hours_elapsed * target_per_hour)

    # What's our remaining target?
    remaining_to_send = max(0, config.TOTAL_DAILY_LIMIT - emails_sent_today)

    # Determine status
    diff = emails_sent_today - target_by_now
    if diff >= 10:
        status = 'ahead'
    elif diff <= -10:
        status = 'behind'
    else:
        status = 'on_track'

    # Calculate adjusted rate
    if remaining_to_send == 0:
        # Already hit daily limit
        adjusted_per_hour = 0
        delay_seconds = 0
        can_send = False
        message = f"Daily limit reached ({emails_sent_today}/{config.TOTAL_DAILY_LIMIT})"
    elif status == 'behind':
        # Catch up: send faster to hit target
        adjusted_per_hour = remaining_to_send / hours_remaining
        # Cap at 2x normal rate to avoid spam triggers
        adjusted_per_hour = min(adjusted_per_hour, target_per_hour * 2)
        delay_seconds = max(3, 3600 / adjusted_per_hour)  # Min 3 sec between emails
        can_send = True
        message = f"Behind schedule ({emails_sent_today}/{target_by_now}). Catching up at {adjusted_per_hour:.0f}/hour"
    elif status == 'ahead':
        # Slow down slightly
        adjusted_per_hour = remaining_to_send / hours_remaining
        # Don't go below 50% of normal rate
        adjusted_per_hour = max(adjusted_per_hour, target_per_hour * 0.5)
        delay_seconds = 3600 / adjusted_per_hour
        can_send = True
        message = f"Ahead of schedule ({emails_sent_today}/{target_by_now}). Maintaining {adjusted_per_hour:.0f}/hour"
    else:
        # On track: maintain steady rate
        adjusted_per_hour = target_per_hour
        delay_seconds = 3600 / adjusted_per_hour  # 90 seconds for 40/hour
        can_send = True
        message = f"On track ({emails_sent_today}/{target_by_now}). Sending {adjusted_per_hour:.0f}/hour"

    return {
        'target_per_hour': round(adjusted_per_hour, 1),
        'delay_seconds': round(delay_seconds, 1),
        'emails_sent_today': emails_sent_today,
        'target_by_now': target_by_now,
        'remaining_to_send': remaining_to_send,
        'hours_remaining': round(hours_remaining, 1),
        'status': status,
        'can_send': can_send,
        'message': message
    }


def display_steady_state_status():
    """Display current steady-state pacing status."""
    pacing = get_steady_state_pacing()

    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  STEADY-STATE PACING STATUS                                ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  Daily Target:        {config.TOTAL_DAILY_LIMIT:<36} ║")
    print(f"║  Sent Today:          {pacing['emails_sent_today']:<36} ║")
    print(f"║  Target by Now:       {pacing['target_by_now']:<36} ║")

    if pacing['status'] != 'outside_hours':
        print(f"║  Remaining:           {pacing['remaining_to_send']:<36} ║")
        print(f"║  Hours Left:          {pacing['hours_remaining']:<36} ║")
        print("║                                                            ║")

        status_icon = {'ahead': '🟢', 'on_track': '✅', 'behind': '🟡'}.get(pacing['status'], '⚪')
        print(f"║  Status: {status_icon} {pacing['message']:<48} ║")
        print("║                                                            ║")
        print(f"║  Current Rate:        {pacing['target_per_hour']} emails/hour{'':<22} ║")
        print(f"║  Delay Between:       {pacing['delay_seconds']} seconds{'':<25} ║")
    else:
        print("║                                                            ║")
        print(f"║  ⏸️  {pacing['message']:<52} ║")

    print("╚════════════════════════════════════════════════════════════╝\n")


def display_rolling_capacity_analysis(analysis: Dict, detailed: bool = True):
    """
    Display rolling capacity analysis in formatted output.

    Args:
        analysis: Dict returned from get_rolling_capacity_analysis()
        detailed: If True, show hour-by-hour breakdown; if False, show compact summary
    """
    emails_last_24h = analysis['emails_in_last_24h']
    current_capacity = analysis['current_capacity']
    total_by_eob = analysis['total_capacity_by_eob']
    will_free = analysis['will_free_by_eob']
    capacity_by_hour = analysis['capacity_by_hour']

    if detailed and capacity_by_hour:
        # Detailed display with hour-by-hour breakdown
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║  ROLLING 24-HOUR CAPACITY ANALYSIS                         ║")
        print("╠════════════════════════════════════════════════════════════╣")
        print(f"║  Daily limit (rolling 24h):       {config.TOTAL_DAILY_LIMIT:<24} ║")
        print(f"║  Sent in last 24 hours:           {emails_last_24h:<24} ║")
        print("║                                                            ║")
        print(f"║  Current capacity available:      {current_capacity:<24} ║")
        if will_free > 0:
            print(f"║  Will free up by end of day:      +{will_free:<23} ║")
        print(f"║  Total sendable by end of day:    {total_by_eob:<24} ║")

        # Show hour-by-hour if we have the data
        if len(capacity_by_hour) > 1:
            print("║                                                            ║")
            print("║  CAPACITY BY HOUR:                                         ║")

            # Sort by time
            sorted_hours = sorted(capacity_by_hour.items())
            prev_capacity = current_capacity

            for hour_time, capacity in sorted_hours[:10]:  # Limit to 10 entries
                hour_str = hour_time.strftime('%I%p').lstrip('0').lower()
                if hour_time == sorted_hours[0][0]:
                    # First entry is "now"
                    print(f"║    {hour_str:<8} (now):  {capacity:>3} available{'':<25} ║")
                else:
                    change = capacity - prev_capacity
                    if change > 0:
                        print(f"║    {hour_str:<8}:       {capacity:>3} available (+{change}){'':<18} ║")
                    else:
                        print(f"║    {hour_str:<8}:       {capacity:>3} available{'':<25} ║")
                prev_capacity = capacity

        print("╚════════════════════════════════════════════════════════════╝\n")

    else:
        # Compact display
        if will_free > 0:
            print(f"✅ Rolling 24h capacity: {current_capacity} now, {total_by_eob} total by end of day (+{will_free} will free up)")
        else:
            print(f"✅ Rolling 24h capacity: {current_capacity} available")

