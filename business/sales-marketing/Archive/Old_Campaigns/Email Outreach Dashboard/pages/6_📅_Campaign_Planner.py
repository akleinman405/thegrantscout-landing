"""
Page 6: Campaign Planner

View today's campaign plan, weekly forecast, and capacity calculator.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import models
from integrations import get_allocation_status, get_daily_summary, get_prospect_stats, get_vertical_status_breakdown
from utils import formatters
from components import campaign_status_table

# Page configuration
st.set_page_config(page_title="Campaign Planner", page_icon="📅", layout="wide")

st.title("📅 Campaign Planner")
st.markdown("Plan and forecast your email campaigns.")
st.markdown("---")

# Get coordination status
try:
    coord_status = get_allocation_status()
except Exception as e:
    st.error(f"Error loading campaign status: {e}")
    coord_status = None

# TODAY'S PLAN
st.header("📋 Today's Plan")

if coord_status:
    # Display date and last updated
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Date", coord_status.get('date', datetime.now().strftime('%Y-%m-%d')))

    with col2:
        if 'last_updated' in coord_status:
            last_updated = coord_status['last_updated']
            st.metric("Last Updated", last_updated[:19] if len(last_updated) > 19 else last_updated)

    with col3:
        status_text = "🟢 Active" if coord_status.get('total_remaining', 0) > 0 else "🔴 Complete"
        st.metric("Status", status_text)

    st.markdown("---")

    # Overall capacity
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Capacity", formatters.format_number(coord_status.get('total_capacity', 0)))
    with col2:
        st.metric("Total Sent", formatters.format_number(coord_status.get('total_sent', 0)))
    with col3:
        st.metric("Remaining", formatters.format_number(coord_status.get('total_remaining', 0)))

    # Progress bar
    total_capacity = coord_status.get('total_capacity', 0)
    total_sent = coord_status.get('total_sent', 0)

    if total_capacity > 0:
        progress = total_sent / total_capacity
        st.progress(min(progress, 1.0))
        st.caption(f"Progress: {progress * 100:.1f}%")

    st.markdown("---")

    # Campaign status table
    campaign_status_table(coord_status)

    st.markdown("---")

    # Vertical breakdown table
    st.subheader("📋 Status by Vertical")

    try:
        vertical_breakdown = get_vertical_status_breakdown()

        if vertical_breakdown:
            # Prepare data for table
            table_data = []
            total_sent = 0
            total_available = 0

            for item in vertical_breakdown:
                table_data.append({
                    'Vertical': item['vertical'],
                    'Campaign Type': item['campaign_type'],
                    'Sent Today': formatters.format_number(item['sent']),
                    'Available': formatters.format_number(item['available']),
                    'Status': item['status']
                })
                total_sent += item['sent']
                total_available += item['available']

            # Add total row
            table_data.append({
                'Vertical': '**TOTAL**',
                'Campaign Type': '**All**',
                'Sent Today': f"**{formatters.format_number(total_sent)}**",
                'Available': f"**{formatters.format_number(total_available)}**",
                'Status': '**--**'
            })

            df = pd.DataFrame(table_data)

            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.caption("""
            **Available prospects:**
            - Initial: Prospects not yet contacted
            - Followup: Prospects who received initial email and are ready for follow-up
            """)

        else:
            st.info("No vertical data available. Configure verticals and upload prospects to see breakdown.")

    except Exception as e:
        st.error(f"Error loading vertical breakdown: {e}")

    # Summary text
    try:
        summary = get_daily_summary()
        if summary:
            st.info(summary)
    except Exception as e:
        st.warning(f"Could not load summary: {e}")

else:
    st.info("""
    No campaign coordination data available yet.

    Coordination data is generated when the email automation scripts run.
    Once you start sending emails, you'll see the daily plan here.
    """)

st.markdown("---")

# WEEKLY FORECAST
st.header("📊 Weekly Forecast (Next 7 Days)")

try:
    # Get email accounts and verticals
    accounts = models.get_email_accounts(active_only=True)
    verticals = models.get_verticals(active_only=True)

    if accounts and verticals:
        # Calculate total daily capacity
        total_daily_capacity = sum(a.get('daily_send_limit', 0) for a in accounts)

        # Get prospect availability
        total_prospects_available = 0
        for vertical in verticals:
            try:
                stats = get_prospect_stats(vertical['vertical_id'])
                total_prospects_available += stats.get('not_contacted', 0)
            except:
                pass

        # Generate 7-day forecast
        forecast_data = []
        current_date = datetime.now().date()

        # Track totals
        total_business_days = 0
        total_planned = 0
        total_remaining = 0

        for day_offset in range(7):
            forecast_date = current_date + timedelta(days=day_offset)

            # Skip weekends
            if forecast_date.weekday() in [5, 6]:  # Saturday, Sunday
                forecast_data.append({
                    'Date': forecast_date.strftime('%Y-%m-%d (%A)'),
                    'Planned Sends': '-- (Weekend)',
                    'Remaining Capacity': '--',
                    'Status': 'Skipped'
                })
            else:
                # Business day
                total_business_days += 1
                planned_sends = min(total_daily_capacity, total_prospects_available)
                remaining_capacity = total_daily_capacity - planned_sends

                # Add to totals
                total_planned += planned_sends
                total_remaining += remaining_capacity

                forecast_data.append({
                    'Date': forecast_date.strftime('%Y-%m-%d (%A)'),
                    'Planned Sends': formatters.format_number(planned_sends),
                    'Remaining Capacity': formatters.format_number(remaining_capacity),
                    'Status': 'Scheduled' if planned_sends > 0 else 'Idle'
                })

                # Reduce available prospects for next day
                total_prospects_available = max(0, total_prospects_available - planned_sends)

        # Add total row
        forecast_data.append({
            'Date': f'**TOTAL ({total_business_days} business days)**',
            'Planned Sends': f'**{formatters.format_number(total_planned)}**',
            'Remaining Capacity': f'**{formatters.format_number(total_remaining)}**',
            'Status': '**--**'
        })

        # Display forecast table
        df = pd.DataFrame(forecast_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Summary
        st.caption(f"""
        **Forecast assumes:**
        - Daily capacity: {formatters.format_number(total_daily_capacity)} emails
        - Business days only (Mon-Fri)
        - Business hours: 9 AM - 3 PM EST
        - Available prospects: Based on current not_contacted count
        """)

    else:
        st.info("Configure email accounts and verticals to see forecast.")

except Exception as e:
    st.error(f"Error generating forecast: {e}")

st.markdown("---")

# CAPACITY CALCULATOR
st.header("🧮 Capacity Calculator")

st.markdown("Calculate how many days you'll need to send to a specific number of prospects.")

col1, col2 = st.columns(2)

with col1:
    prospect_count = st.number_input(
        "Number of Prospects",
        min_value=1,
        max_value=1000000,
        value=1000,
        step=100,
        help="How many prospects do you want to send to?"
    )

with col2:
    # Get current daily capacity
    accounts = models.get_email_accounts(active_only=True)
    daily_capacity = sum(a.get('daily_send_limit', 0) for a in accounts) if accounts else 450

    adjusted_capacity = st.number_input(
        "Daily Capacity",
        min_value=1,
        max_value=10000,
        value=daily_capacity,
        step=50,
        help="Daily sending capacity (defaults to your current account limits)"
    )

if st.button("Calculate", use_container_width=True):
    # Calculate days needed (business days only)
    if adjusted_capacity > 0:
        business_days_needed = (prospect_count + adjusted_capacity - 1) // adjusted_capacity  # Ceiling division

        # Account for weekends
        total_days_needed = business_days_needed
        weeks = business_days_needed // 5
        extra_days = business_days_needed % 5
        total_days_needed = (weeks * 7) + extra_days

        # Calculate end date
        start_date = datetime.now().date()
        end_date = start_date

        days_added = 0
        while days_added < business_days_needed:
            end_date += timedelta(days=1)
            # Only count business days
            if end_date.weekday() < 5:  # Monday = 0, Friday = 4
                days_added += 1

        # Display results
        st.success("✅ Calculation Complete")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Business Days Needed", business_days_needed)
        with col2:
            st.metric("Calendar Days Needed", total_days_needed)
        with col3:
            st.metric("Estimated End Date", end_date.strftime('%Y-%m-%d'))

        # Detailed breakdown
        st.markdown("---")
        st.markdown("### Daily Breakdown")

        breakdown_data = []
        remaining_prospects = prospect_count
        current_date = start_date

        for day_num in range(min(business_days_needed, 30)):  # Show max 30 days
            # Skip to next business day
            while current_date.weekday() >= 5:  # Skip weekends
                current_date += timedelta(days=1)

            sends_today = min(adjusted_capacity, remaining_prospects)
            remaining_prospects -= sends_today

            breakdown_data.append({
                'Day': day_num + 1,
                'Date': current_date.strftime('%Y-%m-%d (%A)'),
                'Sends': formatters.format_number(sends_today),
                'Remaining': formatters.format_number(remaining_prospects)
            })

            current_date += timedelta(days=1)

        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        if business_days_needed > 30:
            st.caption(f"Showing first 30 days. Total business days: {business_days_needed}")

    else:
        st.error("Daily capacity must be greater than 0")

st.markdown("---")

# MANUAL CONTROLS
st.header("🎛️ Manual Controls")

st.warning("⚠️ Manual campaign controls coming soon. For now, manage campaigns through the email scripts.")

col1, col2, col3 = st.columns(3)

with col1:
    st.button("⏸️ Pause Campaign", disabled=True, use_container_width=True, help="Pause all sending")

with col2:
    st.button("▶️ Resume Campaign", disabled=True, use_container_width=True, help="Resume sending")

with col3:
    st.button("⏭️ Skip Today", disabled=True, use_container_width=True, help="Skip remaining sends for today")

st.caption("""
Manual controls will be implemented in a future update.
For now, you can stop the Python email scripts to pause campaigns.
""")

# Refresh button
st.markdown("---")
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
