"""
Table components for displaying data in structured formats.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from utils import formatters


def prospects_table(df: pd.DataFrame, editable: bool = False, show_actions: bool = True):
    """
    Display prospects data table.

    Args:
        df: DataFrame with prospect data
        editable: Whether to allow editing
        show_actions: Whether to show action buttons
    """
    if df.empty:
        st.info("No prospects found.")
        return

    # Format columns for display
    display_df = df.copy()

    # Rename columns for better display
    column_config = {
        'email': st.column_config.TextColumn('Email', width='medium'),
        'first_name': st.column_config.TextColumn('First Name', width='small'),
        'company_name': st.column_config.TextColumn('Company', width='medium'),
        'state': st.column_config.TextColumn('State', width='small'),
        'website': st.column_config.TextColumn('Website', width='medium'),
    }

    # Add status columns if they exist
    if 'initial_sent' in df.columns:
        column_config['initial_sent'] = st.column_config.CheckboxColumn('Initial Sent', width='small')
    if 'followup_sent' in df.columns:
        column_config['followup_sent'] = st.column_config.CheckboxColumn('Follow-up Sent', width='small')
    if 'responded' in df.columns:
        column_config['responded'] = st.column_config.CheckboxColumn('Responded', width='small')

    # Display dataframe
    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config=column_config,
        height=400
    )


def accounts_table(accounts: List[Dict[str, Any]], show_actions: bool = True):
    """
    Display email accounts table.

    Args:
        accounts: List of account dictionaries
        show_actions: Whether to show action buttons
    """
    if not accounts:
        st.info("No email accounts configured.")
        return

    # Prepare data for display
    table_data = []
    for account in accounts:
        status = "✅ Active" if account.get('active') else "❌ Inactive"
        sent_today = account.get('sent_today', 0)
        daily_limit = account.get('daily_send_limit', 0)
        quota_pct = (sent_today / daily_limit * 100) if daily_limit > 0 else 0

        table_data.append({
            'Email': account.get('email_address', ''),
            'Display Name': account.get('display_name', ''),
            'Status': status,
            'Sent Today': f"{sent_today:,}",
            'Daily Limit': f"{daily_limit:,}",
            'Quota %': f"{quota_pct:.1f}%",
            'SMTP': f"{account.get('smtp_host', '')}:{account.get('smtp_port', '')}",
        })

    df = pd.DataFrame(table_data)

    # Display table
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        height=400
    )


def verticals_table(verticals: List[Dict[str, Any]], prospect_counts: Dict[str, int] = None, show_actions: bool = True):
    """
    Display verticals table.

    Args:
        verticals: List of vertical dictionaries
        prospect_counts: Dict mapping vertical_id to prospect count
        show_actions: Whether to show action buttons
    """
    if not verticals:
        st.info("No verticals configured.")
        return

    # Prepare data for display
    table_data = []
    for vertical in verticals:
        vertical_id = vertical.get('vertical_id', '')
        status = "✅ Active" if vertical.get('active') else "❌ Inactive"
        count = prospect_counts.get(vertical_id, 0) if prospect_counts else 0

        table_data.append({
            'Vertical ID': vertical_id,
            'Display Name': vertical.get('display_name', ''),
            'Target Industry': vertical.get('target_industry', ''),
            'Prospects': f"{count:,}",
            'Status': status,
            'CSV File': vertical.get('csv_filename', ''),
        })

    df = pd.DataFrame(table_data)

    # Display table
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        height=400
    )


def templates_table(templates: List[Dict[str, Any]], show_actions: bool = True):
    """
    Display templates table.

    Args:
        templates: List of template dictionaries
        show_actions: Whether to show action buttons
    """
    if not templates:
        st.info("No templates found.")
        return

    # Prepare data for display
    table_data = []
    for template in templates:
        status = "✅ Active" if template.get('active') else "❌ Inactive"
        template_type = template.get('template_type', '').title()
        subject_preview = template.get('subject_line', '')[:50]
        if len(template.get('subject_line', '')) > 50:
            subject_preview += '...'

        table_data.append({
            'Name': template.get('template_name', ''),
            'Type': template_type,
            'Subject': subject_preview,
            'Status': status,
            'Created': template.get('created_at', '')[:10] if template.get('created_at') else '',
        })

    df = pd.DataFrame(table_data)

    # Display table
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        height=400
    )


def campaign_status_table(status_data: Dict[str, Any]):
    """
    Display campaign status table from coordination data.

    Args:
        status_data: Coordination status dictionary
    """
    if not status_data:
        st.warning("No campaign status data available.")
        return

    # Prepare data
    table_data = []

    # Initial campaign
    if 'initial' in status_data:
        initial = status_data['initial']
        table_data.append({
            'Campaign': 'Initial Outreach',
            'Allocated': f"{initial.get('allocated', 0):,}",
            'Sent': f"{initial.get('sent', 0):,}",
            'Remaining': f"{initial.get('remaining', 0):,}",
            'Status': initial.get('status', 'unknown').upper(),
        })

    # Follow-up campaign
    if 'followup' in status_data:
        followup = status_data['followup']
        table_data.append({
            'Campaign': 'Follow-up',
            'Allocated': f"{followup.get('allocated', 0):,}",
            'Sent': f"{followup.get('sent', 0):,}",
            'Remaining': f"{followup.get('remaining', 0):,}",
            'Status': followup.get('status', 'unknown').upper(),
        })

    df = pd.DataFrame(table_data)

    # Display table
    st.dataframe(
        df,
        width='stretch',
        hide_index=True
    )


def assignment_matrix(accounts: List[Dict], verticals: List[Dict], assignments: Dict[int, List[str]]):
    """
    Display account-vertical assignment matrix.

    Args:
        accounts: List of email account dictionaries
        verticals: List of vertical dictionaries
        assignments: Dict mapping account_id to list of assigned vertical_ids
    """
    if not accounts or not verticals:
        st.info("No accounts or verticals to display.")
        return

    st.markdown("### Account-Vertical Assignment Matrix")
    st.caption("Shows which email accounts are assigned to which verticals")

    # Create matrix display
    matrix_data = []
    for account in accounts:
        account_id = account.get('account_id')
        row = {
            'Account': account.get('email_address', 'Unknown')
        }

        assigned = assignments.get(account_id, [])

        for vertical in verticals:
            vertical_id = vertical.get('vertical_id')
            row[vertical.get('display_name', vertical_id)] = '✅' if vertical_id in assigned else '❌'

        matrix_data.append(row)

    df = pd.DataFrame(matrix_data)

    # Display matrix
    st.dataframe(
        df,
        width='stretch',
        hide_index=True
    )
