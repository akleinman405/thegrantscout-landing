"""
Card components for displaying metrics and information.
"""

import streamlit as st
from typing import Optional, Dict, Any


def metric_card(title: str, value: Any, delta: Optional[str] = None, icon: Optional[str] = None):
    """
    Display a metric card with optional icon and delta.

    Args:
        title: Metric label
        value: Metric value
        delta: Optional delta/change indicator
        icon: Optional emoji icon
    """
    if icon:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown(f"<div style='font-size: 2.5em;'>{icon}</div>", unsafe_allow_html=True)
        with col2:
            st.metric(label=title, value=value, delta=delta)
    else:
        st.metric(label=title, value=value, delta=delta)


def status_card(title: str, status: str, color: str, details: Optional[str] = None):
    """
    Display a status card with colored badge.

    Args:
        title: Card title
        status: Status text
        color: Badge color (green, yellow, red, blue)
        details: Optional details text
    """
    color_map = {
        'green': '#28a745',
        'yellow': '#ffc107',
        'red': '#dc3545',
        'blue': '#007bff',
        'gray': '#6c757d'
    }

    bg_color = color_map.get(color, '#6c757d')

    html = f"""
    <div style="padding: 1em; border-radius: 0.5em; background-color: #f8f9fa; border-left: 4px solid {bg_color};">
        <h4 style="margin: 0;">{title}</h4>
        <span style="display: inline-block; padding: 0.25em 0.6em; background-color: {bg_color};
                     color: white; border-radius: 0.25em; font-size: 0.9em; margin-top: 0.5em;">
            {status}
        </span>
        {f'<p style="margin-top: 0.5em; margin-bottom: 0; color: #6c757d;">{details}</p>' if details else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def info_card(title: str, content: str, icon: Optional[str] = None):
    """
    Display an informational card.

    Args:
        title: Card title
        content: Card content
        icon: Optional emoji icon
    """
    icon_html = f"<span style='font-size: 1.5em; margin-right: 0.5em;'>{icon}</span>" if icon else ""

    html = f"""
    <div style="padding: 1em; border-radius: 0.5em; background-color: #e7f3ff; border: 1px solid #b3d9ff;">
        <h4 style="margin: 0;">{icon_html}{title}</h4>
        <p style="margin-top: 0.5em; margin-bottom: 0;">{content}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def account_card(account_info: Dict[str, Any]):
    """
    Display an email account card with quota information.

    Args:
        account_info: Dictionary with account details (email, daily_limit, sent_today, status, etc.)
    """
    email = account_info.get('email_address', 'Unknown')
    display_name = account_info.get('display_name', '')
    daily_limit = account_info.get('daily_send_limit', 0)
    sent_today = account_info.get('sent_today', 0)
    active = account_info.get('active', 0)

    status_color = '#28a745' if active else '#6c757d'
    status_text = 'Active' if active else 'Inactive'

    progress_pct = (sent_today / daily_limit * 100) if daily_limit > 0 else 0
    progress_color = '#28a745' if progress_pct < 75 else ('#ffc107' if progress_pct < 90 else '#dc3545')

    html = f"""
    <div style="padding: 1em; border-radius: 0.5em; background-color: #f8f9fa; border: 1px solid #dee2e6;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">{display_name or email}</h4>
                <p style="margin: 0.25em 0; color: #6c757d; font-size: 0.9em;">{email if display_name else ''}</p>
            </div>
            <span style="padding: 0.25em 0.6em; background-color: {status_color};
                         color: white; border-radius: 0.25em; font-size: 0.9em;">
                {status_text}
            </span>
        </div>
        <div style="margin-top: 1em;">
            <div style="display: flex; justify-content: space-between; font-size: 0.9em; margin-bottom: 0.25em;">
                <span>Daily Quota</span>
                <span><strong>{sent_today}</strong> / {daily_limit}</span>
            </div>
            <div style="width: 100%; background-color: #e9ecef; border-radius: 0.25em; height: 8px;">
                <div style="width: {min(progress_pct, 100)}%; background-color: {progress_color};
                            height: 100%; border-radius: 0.25em;"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def vertical_card(vertical_info: Dict[str, Any], prospect_count: int = 0):
    """
    Display a vertical card with statistics.

    Args:
        vertical_info: Dictionary with vertical details
        prospect_count: Number of prospects for this vertical
    """
    vertical_id = vertical_info.get('vertical_id', 'Unknown')
    display_name = vertical_info.get('display_name', 'Unknown')
    target_industry = vertical_info.get('target_industry', '')
    active = vertical_info.get('active', 0)

    status_color = '#28a745' if active else '#6c757d'
    status_text = 'Active' if active else 'Inactive'

    html = f"""
    <div style="padding: 1em; border-radius: 0.5em; background-color: #f8f9fa; border: 1px solid #dee2e6;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0;">{display_name}</h4>
                <p style="margin: 0.25em 0; color: #6c757d; font-size: 0.9em;">{vertical_id}</p>
                {f'<p style="margin: 0.25em 0; color: #6c757d; font-size: 0.85em;"><em>{target_industry}</em></p>' if target_industry else ''}
            </div>
            <span style="padding: 0.25em 0.6em; background-color: {status_color};
                         color: white; border-radius: 0.25em; font-size: 0.9em;">
                {status_text}
            </span>
        </div>
        <div style="margin-top: 1em; padding-top: 1em; border-top: 1px solid #dee2e6;">
            <span style="font-size: 0.9em; color: #6c757d;">Prospects:</span>
            <span style="font-size: 1.5em; font-weight: bold; color: #007bff; margin-left: 0.5em;">
                {prospect_count:,}
            </span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
