"""
Reusable form components for data entry and editing.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from database import models
from utils import validators


def email_account_form(account: Optional[Dict[str, Any]] = None, verticals: Optional[List[Dict]] = None) -> Optional[Dict]:
    """
    Display form for creating/editing email account.

    Args:
        account: Existing account data for editing (None for new account)
        verticals: List of available verticals for assignment

    Returns:
        Dict with form data if submitted, None otherwise
    """
    is_edit = account is not None

    with st.form("email_account_form"):
        st.subheader("Email Account" if not is_edit else f"Edit Account: {account.get('email_address', '')}")

        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input(
                "Email Address *",
                value=account.get('email_address', '') if account else '',
                help="The email address that will send emails"
            )

            smtp_host = st.text_input(
                "SMTP Host *",
                value=account.get('smtp_host', 'smtp.gmail.com') if account else 'smtp.gmail.com',
                help="e.g., smtp.gmail.com, smtp.office365.com"
            )

            smtp_username = st.text_input(
                "SMTP Username *",
                value=account.get('smtp_username', '') if account else '',
                help="Usually the same as email address"
            )

        with col2:
            display_name = st.text_input(
                "Display Name",
                value=account.get('display_name', '') if account else '',
                help="Friendly name for this account (optional)"
            )

            smtp_port = st.number_input(
                "SMTP Port *",
                min_value=1,
                max_value=65535,
                value=int(account.get('smtp_port', 587)) if account else 587,
                help="Common: 587 (TLS), 465 (SSL), 25 (unencrypted)"
            )

            daily_limit = st.number_input(
                "Daily Send Limit *",
                min_value=1,
                max_value=10000,
                value=int(account.get('daily_send_limit', 450)) if account else 450,
                help="Maximum emails per day for this account"
            )

        password = st.text_input(
            "Password *",
            type="password",
            help="Password or app-specific password for SMTP authentication"
        )

        if not is_edit and not password:
            st.warning("Password is required for new accounts")

        active = st.checkbox(
            "Active",
            value=bool(account.get('active', 1)) if account else True,
            help="Only active accounts will be used for sending"
        )

        # Vertical assignments
        if verticals:
            st.markdown("---")
            st.subheader("Vertical Assignments")
            st.caption("Select which verticals this account can send for")

            assigned_verticals = []
            if account:
                # Get current assignments
                current_assignments = models.get_account_verticals(account.get('account_id'))
                assigned_verticals = current_assignments if current_assignments else []

            selected_verticals = []
            for vertical in verticals:
                if st.checkbox(
                    f"{vertical['display_name']} ({vertical['vertical_id']})",
                    value=vertical['vertical_id'] in assigned_verticals,
                    key=f"vertical_{vertical['vertical_id']}"
                ):
                    selected_verticals.append(vertical['vertical_id'])

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 Save Account", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            return None

        if submitted:
            # Validate
            if not email or not smtp_host or not smtp_username or not daily_limit:
                st.error("Please fill in all required fields (*)")
                return None

            if not validators.validate_email(email):
                st.error("Invalid email address format")
                return None

            if not password and not is_edit:
                st.error("Password is required for new accounts")
                return None

            return {
                'email_address': email,
                'display_name': display_name,
                'smtp_host': smtp_host,
                'smtp_port': smtp_port,
                'smtp_username': smtp_username,
                'password': password if password else None,
                'daily_send_limit': daily_limit,
                'active': active,
                'verticals': selected_verticals if verticals else []
            }

    return None


def vertical_form(vertical: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
    """
    Display form for creating/editing vertical.

    Args:
        vertical: Existing vertical data for editing (None for new vertical)

    Returns:
        Dict with form data if submitted, None otherwise
    """
    is_edit = vertical is not None

    with st.form("vertical_form"):
        st.subheader("New Vertical" if not is_edit else f"Edit Vertical: {vertical.get('display_name', '')}")

        col1, col2 = st.columns(2)

        with col1:
            vertical_id = st.text_input(
                "Vertical ID *",
                value=vertical.get('vertical_id', '') if vertical else '',
                disabled=is_edit,  # Cannot change ID after creation
                help="Unique identifier (e.g., IDEA_078, debarment). Use only letters, numbers, underscores."
            )

            target_industry = st.text_input(
                "Target Industry",
                value=vertical.get('target_industry', '') if vertical else '',
                help="e.g., Federal Contractors, Restaurants, Nonprofits"
            )

        with col2:
            display_name = st.text_input(
                "Display Name *",
                value=vertical.get('display_name', '') if vertical else '',
                help="Human-readable name (e.g., Debarment Monitor)"
            )

            active = st.checkbox(
                "Active",
                value=bool(vertical.get('active', 1)) if vertical else True,
                help="Only active verticals appear in dashboards"
            )

        csv_filename = st.text_input(
            "CSV Filename",
            value=vertical.get('csv_filename', '') if vertical else '',
            help="Filename for prospect CSV (e.g., debarment_prospects.csv). Leave blank to auto-generate."
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 Save Vertical", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            return None

        if submitted:
            # Validate
            if not vertical_id or not display_name:
                st.error("Please fill in all required fields (*)")
                return None

            if not validators.validate_vertical_id(vertical_id):
                st.error("Invalid vertical ID format. Use only letters, numbers, and underscores.")
                return None

            # Auto-generate CSV filename if not provided
            if not csv_filename:
                csv_filename = f"{vertical_id}_prospects.csv"

            return {
                'vertical_id': vertical_id,
                'display_name': display_name,
                'target_industry': target_industry,
                'csv_filename': csv_filename,
                'active': active
            }

    return None


def template_editor_form(template: Optional[Dict[str, Any]] = None, vertical_id: Optional[str] = None) -> Optional[Dict]:
    """
    Display form for editing email template.

    Args:
        template: Existing template data for editing (None for new template)
        vertical_id: Vertical ID for new template

    Returns:
        Dict with form data if submitted, None otherwise
    """
    is_edit = template is not None

    with st.form("template_editor_form"):
        st.subheader("New Template" if not is_edit else "Edit Template")

        col1, col2 = st.columns(2)

        with col1:
            template_name = st.text_input(
                "Template Name *",
                value=template.get('template_name', '') if template else '',
                help="Descriptive name for this template"
            )

        with col2:
            template_type = st.selectbox(
                "Template Type *",
                options=['initial', 'followup'],
                index=0 if not template else (['initial', 'followup'].index(template.get('template_type', 'initial'))),
                help="Initial outreach or follow-up email"
            )

        subject_line = st.text_input(
            "Subject Line *",
            value=template.get('subject_line', '') if template else '',
            help="Email subject line (can use variables like {company}, {first_name})"
        )

        email_body = st.text_area(
            "Email Body *",
            value=template.get('email_body', '') if template else '',
            height=300,
            help="Email body content. Available variables: {greeting}, {first_name}, {company_name}, {state}, {website}"
        )

        # Show available variables
        with st.expander("📝 Available Template Variables"):
            st.markdown("""
            - `{greeting}` - Personalized greeting (e.g., " John" or "")
            - `{first_name}` - Prospect's first name
            - `{company_name}` - Company name
            - `{state}` - State abbreviation
            - `{website}` - Company website

            **Example:**
            ```
            Subject: Important alert for {company_name}

            Hi{greeting},

            I noticed that {company_name} in {state} might be interested in...
            ```
            """)

        # Live preview
        st.markdown("---")
        st.subheader("📧 Preview")

        preview_data = {
            'greeting': ' John',
            'first_name': 'John',
            'company_name': 'Acme Corp',
            'state': 'CA',
            'website': 'www.acmecorp.com'
        }

        try:
            preview_subject = subject_line.format(**preview_data) if subject_line else ''
            preview_body = email_body.format(**preview_data) if email_body else ''

            st.text(f"Subject: {preview_subject}")
            st.text_area("Body Preview", preview_body, height=200, disabled=True)
        except KeyError as e:
            st.warning(f"Invalid variable in template: {e}")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 Save Template", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            return None

        if submitted:
            # Validate
            if not template_name or not subject_line or not email_body:
                st.error("Please fill in all required fields (*)")
                return None

            return {
                'template_name': template_name,
                'template_type': template_type,
                'subject_line': subject_line,
                'email_body': email_body,
                'vertical_id': vertical_id if not is_edit else template.get('vertical_id')
            }

    return None


def settings_form(current_settings: Dict[str, str]) -> Optional[Dict]:
    """
    Display settings form.

    Args:
        current_settings: Current settings values

    Returns:
        Dict with updated settings if submitted, None otherwise
    """
    with st.form("settings_form"):
        st.subheader("Global Campaign Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Business Hours")
            business_hours_start = st.number_input(
                "Start Hour (0-23)",
                min_value=0,
                max_value=23,
                value=int(current_settings.get('business_hours_start', 9)),
                help="Campaign starts sending at this hour (EST)"
            )

            business_hours_end = st.number_input(
                "End Hour (0-23)",
                min_value=0,
                max_value=23,
                value=int(current_settings.get('business_hours_end', 15)),
                help="Campaign stops sending at this hour (EST)"
            )

        with col2:
            st.markdown("#### Pacing Settings")
            timezone = st.text_input(
                "Timezone",
                value=current_settings.get('timezone', 'US/Eastern'),
                help="Timezone for business hours"
            )

            conservative_pacing = st.checkbox(
                "Conservative Pacing Mode",
                value=current_settings.get('conservative_pacing', 'true') == 'true',
                help="Add extra delays between emails to be more conservative"
            )

        st.markdown("---")
        st.subheader("Anti-Spam Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            base_delay_min = st.number_input(
                "Min Delay (seconds)",
                min_value=1,
                max_value=300,
                value=int(current_settings.get('base_delay_min', 5)),
                help="Minimum delay between emails"
            )

        with col2:
            base_delay_max = st.number_input(
                "Max Delay (seconds)",
                min_value=1,
                max_value=300,
                value=int(current_settings.get('base_delay_max', 10)),
                help="Maximum delay between emails"
            )

        with col3:
            break_frequency = st.number_input(
                "Break Frequency",
                min_value=1,
                max_value=1000,
                value=int(current_settings.get('break_frequency', 50)),
                help="Take a break after this many emails"
            )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
        with col2:
            reset = st.form_submit_button("Reset to Defaults", use_container_width=True)

        if reset:
            return {
                'business_hours_start': '9',
                'business_hours_end': '15',
                'timezone': 'US/Eastern',
                'conservative_pacing': 'true',
                'base_delay_min': '5',
                'base_delay_max': '10',
                'break_frequency': '50'
            }

        if submitted:
            # Validate
            if business_hours_start >= business_hours_end:
                st.error("Start hour must be before end hour")
                return None

            return {
                'business_hours_start': str(business_hours_start),
                'business_hours_end': str(business_hours_end),
                'timezone': timezone,
                'conservative_pacing': 'true' if conservative_pacing else 'false',
                'base_delay_min': str(base_delay_min),
                'base_delay_max': str(base_delay_max),
                'break_frequency': str(break_frequency)
            }

    return None
