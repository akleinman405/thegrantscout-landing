"""
Chart components using Plotly for interactive visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


def line_chart_emails_over_time(df: pd.DataFrame, vertical_filter: str = 'all', days: int = 30):
    """
    Display line chart of emails sent over time.

    Args:
        df: DataFrame with columns: date, vertical (from sent_tracker)
        vertical_filter: 'all' or specific vertical ID
        days: Number of days to show
    """
    if df.empty:
        st.info("No sent email data available yet.")
        return

    # Filter by vertical
    if vertical_filter != 'all':
        df = df[df['vertical'] == vertical_filter].copy()

    # Ensure date column is datetime
    if 'date' not in df.columns:
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
        else:
            st.warning("No date column found in data")
            return

    # Group by date
    daily = df.groupby('date').size().reset_index(name='count')
    daily['date'] = pd.to_datetime(daily['date'])

    # Filter to last N days
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    daily = daily[daily['date'] >= cutoff]

    if daily.empty:
        st.info(f"No data in the last {days} days.")
        return

    # Create line chart
    fig = px.line(
        daily,
        x='date',
        y='count',
        title=f'Emails Sent Over Time ({days} days)',
        labels={'date': 'Date', 'count': 'Emails Sent'},
        markers=True
    )

    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)


def bar_chart_by_vertical(df: pd.DataFrame, title: str = "Emails by Vertical"):
    """
    Display bar chart showing email counts by vertical.

    Args:
        df: DataFrame with 'vertical' column
        title: Chart title
    """
    if df.empty:
        st.info("No data available.")
        return

    # Group by vertical
    vertical_counts = df.groupby('vertical').size().reset_index(name='count')
    vertical_counts = vertical_counts.sort_values('count', ascending=False)

    # Create bar chart
    fig = px.bar(
        vertical_counts,
        x='vertical',
        y='count',
        title=title,
        labels={'vertical': 'Vertical', 'count': 'Emails Sent'},
        color='count',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)


def donut_chart_response_rates(breakdown_data: list):
    """
    Display donut chart showing response rates by vertical.

    Args:
        breakdown_data: List of dicts with 'vertical', 'sent_total', 'response_rate'
    """
    if not breakdown_data:
        st.info("No response data available.")
        return

    # Prepare data
    df = pd.DataFrame(breakdown_data)

    if df.empty or 'vertical' not in df.columns:
        st.info("No response data available.")
        return

    # Calculate responses
    df['responses'] = (df['sent_total'] * df['response_rate']).astype(int)
    df['no_response'] = df['sent_total'] - df['responses']

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=df['vertical'],
        values=df['responses'],
        hole=.4,
        textinfo='label+percent',
        textposition='outside',
        marker=dict(colors=px.colors.qualitative.Set3)
    )])

    fig.update_layout(
        title='Response Distribution by Vertical',
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)


def progress_bar_quota(sent: int, limit: int, label: str = "Quota Usage"):
    """
    Display progress bar for quota usage.

    Args:
        sent: Number sent
        limit: Total limit
        label: Label text
    """
    if limit <= 0:
        st.warning("No limit set")
        return

    pct = (sent / limit) * 100
    color = 'normal' if pct < 75 else ('orange' if pct < 90 else 'red')

    # Use Streamlit's progress bar
    st.progress(min(sent / limit, 1.0))
    st.caption(f"{label}: {sent:,} / {limit:,} ({pct:.1f}%)")


def stacked_bar_chart_campaign_status(initial_data: dict, followup_data: dict):
    """
    Display stacked bar chart comparing initial and follow-up campaigns.

    Args:
        initial_data: Dict with 'allocated', 'sent', 'remaining'
        followup_data: Dict with 'allocated', 'sent', 'remaining'
    """
    # Prepare data
    campaigns = ['Initial', 'Follow-up']
    sent = [initial_data.get('sent', 0), followup_data.get('sent', 0)]
    remaining = [initial_data.get('remaining', 0), followup_data.get('remaining', 0)]

    # Create stacked bar chart
    fig = go.Figure(data=[
        go.Bar(name='Sent', x=campaigns, y=sent, marker_color='#28a745'),
        go.Bar(name='Remaining', x=campaigns, y=remaining, marker_color='#6c757d')
    ])

    fig.update_layout(
        barmode='stack',
        title='Campaign Progress',
        yaxis_title='Emails',
        xaxis_title='Campaign Type',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)


def gauge_chart_capacity(used: int, total: int):
    """
    Display gauge chart for capacity usage.

    Args:
        used: Capacity used
        total: Total capacity
    """
    if total <= 0:
        st.warning("No capacity configured")
        return

    pct = (used / total) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Capacity Used (%)"},
        delta={'reference': 75},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)
