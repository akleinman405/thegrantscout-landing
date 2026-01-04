"""
Page 1: Dashboard (Home)

Displays campaign overview, metrics, and status.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import models
from integrations import (
    get_daily_metrics,
    get_vertical_breakdown,
    get_allocation_status,
    read_sent_tracker
)
from utils import formatters
from components import (
    metric_card,
    line_chart_emails_over_time,
    bar_chart_by_vertical,
    donut_chart_response_rates,
    campaign_status_table,
    stacked_bar_chart_campaign_status
)

# Page configuration
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Campaign Dashboard")
st.markdown("---")

# Filters
col1, col2 = st.columns(2)

with col1:
    # Vertical filter
    verticals = models.get_verticals(active_only=True)
    vertical_options = ['all'] + [v['vertical_id'] for v in verticals]
    vertical_labels = ['All Verticals'] + [f"{v['display_name']} ({v['vertical_id']})" for v in verticals]

    selected_vertical = st.selectbox(
        "Filter by Vertical",
        options=vertical_options,
        format_func=lambda x: vertical_labels[vertical_options.index(x)],
        key='vertical_filter'
    )

with col2:
    # Time period filter
    time_period = st.selectbox(
        "Time Period",
        options=['day', 'week', 'month', 'total'],
        format_func=lambda x: x.title(),
        key='time_period'
    )

st.markdown("---")

# Get metrics based on time period and vertical
try:
    sent_df = read_sent_tracker()

    # Filter by vertical if selected
    if selected_vertical != 'all' and not sent_df.empty:
        sent_df = sent_df[sent_df['vertical'] == selected_vertical]

    # Calculate metrics based on time period
    today = datetime.now().date()
    total_sent = 0
    total_received = 0

    if not sent_df.empty:
        if 'timestamp' in sent_df.columns:
            sent_df['date'] = pd.to_datetime(sent_df['timestamp']).dt.date

            if time_period == 'day':
                filtered_df = sent_df[sent_df['date'] == today]
            elif time_period == 'week':
                week_ago = today - timedelta(days=7)
                filtered_df = sent_df[sent_df['date'] >= week_ago]
            elif time_period == 'month':
                month_ago = today - timedelta(days=30)
                filtered_df = sent_df[sent_df['date'] >= month_ago]
            else:  # total
                filtered_df = sent_df

            total_sent = len(filtered_df)

    # Get response metrics from response tracker
    from integrations import read_response_tracker
    response_df = read_response_tracker()

    if not response_df.empty:
        if selected_vertical != 'all' and 'vertical' in response_df.columns:
            response_df = response_df[response_df['vertical'] == selected_vertical]

        # Count actual responses (not PENDING)
        if 'replied' in response_df.columns:
            total_received = len(response_df[response_df['replied'] != 'PENDING'])
        else:
            total_received = 0

    response_rate = (total_received / total_sent * 100) if total_sent > 0 else 0.0

    metrics = {
        'sent': total_sent,
        'received': total_received,
        'response_rate': response_rate
    }

    vertical_breakdown = get_vertical_breakdown()
except Exception as e:
    st.error(f"Error loading metrics: {e}")
    metrics = {
        'sent': 0,
        'received': 0,
        'response_rate': 0.0
    }
    vertical_breakdown = []

# Top Metrics Row
st.subheader(f"Key Metrics - {time_period.title()}")

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Emails Sent",
        formatters.format_number(metrics.get('sent', 0)),
        icon="📧"
    )

with col2:
    metric_card(
        "Responses Received",
        formatters.format_number(metrics.get('received', 0)),
        icon="💬"
    )

with col3:
    metric_card(
        "Response Rate",
        f"{metrics.get('response_rate', 0):.1f}%",
        icon="📊"
    )

st.markdown("---")

# Charts Section
st.subheader("Performance Analytics")

# Line chart - Emails over time
try:
    sent_df = read_sent_tracker()
    if not sent_df.empty:
        # Set days based on time period
        days_map = {
            'day': 1,
            'week': 7,
            'month': 30,
            'total': 365  # Show last year for "total"
        }
        days = days_map.get(time_period, 30)

        line_chart_emails_over_time(sent_df, vertical_filter=selected_vertical, days=days)
    else:
        st.info("No sent email data available yet. Start sending emails to see charts here.")
except Exception as e:
    st.error(f"Error loading chart data: {e}")

st.markdown("---")

# Bar chart and donut chart side-by-side
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Emails by Vertical ({time_period.title()})")
    try:
        sent_df = read_sent_tracker()
        if not sent_df.empty:
            # Filter based on time period
            today = datetime.now().date()
            if 'timestamp' in sent_df.columns:
                sent_df['date'] = pd.to_datetime(sent_df['timestamp']).dt.date

                if time_period == 'day':
                    period_df = sent_df[sent_df['date'] == today]
                elif time_period == 'week':
                    week_ago = today - timedelta(days=7)
                    period_df = sent_df[sent_df['date'] >= week_ago]
                elif time_period == 'month':
                    month_ago = today - timedelta(days=30)
                    period_df = sent_df[sent_df['date'] >= month_ago]
                else:  # total
                    period_df = sent_df

                if not period_df.empty:
                    bar_chart_by_vertical(period_df, title=f"{time_period.title()} Sends by Vertical")
                else:
                    st.info(f"No emails sent in this {time_period} yet.")
            else:
                st.warning("No timestamp data available.")
        else:
            st.info("No sent email data available.")
    except Exception as e:
        st.error(f"Error loading chart: {e}")

with col2:
    st.subheader("Response Rates")
    try:
        if vertical_breakdown:
            donut_chart_response_rates(vertical_breakdown)
        else:
            st.info("No response data available yet.")
    except Exception as e:
        st.error(f"Error loading response chart: {e}")

st.markdown("---")

# Email Account Status
st.subheader("Email Account Status")

try:
    accounts = models.get_email_accounts(active_only=False)

    if accounts:
        # Display account cards
        cols = st.columns(min(3, len(accounts)))

        for idx, account in enumerate(accounts):
            with cols[idx % 3]:
                # Get sent count for today
                sent_today = 0
                sent_df = read_sent_tracker()
                if not sent_df.empty and 'from_email' in sent_df.columns:
                    today = datetime.now().date()
                    if 'timestamp' in sent_df.columns:
                        sent_df['date'] = pd.to_datetime(sent_df['timestamp']).dt.date
                        today_df = sent_df[
                            (sent_df['date'] == today) &
                            (sent_df['from_email'] == account['email_address'])
                        ]
                        sent_today = len(today_df)

                # Add sent_today to account dict
                account['sent_today'] = sent_today

                # Display account card
                from components.cards import account_card
                account_card(account)
    else:
        st.info("No email accounts configured. Go to Email Accounts page to add accounts.")

except Exception as e:
    st.error(f"Error loading email accounts: {e}")

st.markdown("---")

# Campaign Status
st.subheader("Campaign Status")

try:
    coord_status = get_allocation_status()

    if coord_status:
        # Display status cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Capacity",
                formatters.format_number(coord_status.get('total_capacity', 0))
            )

        with col2:
            st.metric(
                "Total Sent Today",
                formatters.format_number(coord_status.get('total_sent', 0))
            )

        with col3:
            st.metric(
                "Remaining",
                formatters.format_number(coord_status.get('total_remaining', 0))
            )

        # Campaign status table
        campaign_status_table(coord_status)

        # Stacked bar chart
        if 'initial' in coord_status and 'followup' in coord_status:
            from components.charts import stacked_bar_chart_campaign_status
            stacked_bar_chart_campaign_status(
                coord_status['initial'],
                coord_status['followup']
            )

        # Display last updated
        if 'last_updated' in coord_status:
            st.caption(f"Last updated: {coord_status['last_updated']}")

    else:
        st.info("No campaign coordination data available. Coordination data is generated when email scripts run.")

except Exception as e:
    st.error(f"Error loading campaign status: {e}")

# Refresh button
st.markdown("---")
if st.button("🔄 Refresh Dashboard", use_container_width=True):
    from integrations.tracker_reader import clear_cache
    clear_cache()
    st.cache_data.clear()
    st.rerun()
