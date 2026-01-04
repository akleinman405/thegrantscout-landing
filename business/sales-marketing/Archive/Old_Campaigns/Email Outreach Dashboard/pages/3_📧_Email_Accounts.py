"""
Page 3: Email Accounts

Manage email accounts, SMTP settings, and vertical assignments.
"""

import streamlit as st
from database import models
from utils import validators, formatters
from components import email_account_form, accounts_table, assignment_matrix

# Page configuration
st.set_page_config(page_title="Email Accounts", page_icon="📧", layout="wide")

st.title("📧 Email Accounts")
st.markdown("Manage email accounts, SMTP settings, and vertical assignments.")
st.markdown("---")

# Get accounts and verticals
accounts = models.get_email_accounts(active_only=False)
verticals = models.get_verticals(active_only=True)

# Session state for form display
if 'show_account_form' not in st.session_state:
    st.session_state.show_account_form = False
if 'edit_account_id' not in st.session_state:
    st.session_state.edit_account_id = None

# Summary metrics
if accounts:
    col1, col2, col3, col4 = st.columns(4)

    active_count = sum(1 for a in accounts if a.get('active'))
    total_capacity = sum(a.get('daily_send_limit', 0) for a in accounts if a.get('active'))

    with col1:
        st.metric("Total Accounts", len(accounts))
    with col2:
        st.metric("Active Accounts", active_count)
    with col3:
        st.metric("Total Daily Capacity", formatters.format_number(total_capacity))
    with col4:
        # Calculate sent today (would need to query sent_tracker)
        st.metric("Sent Today", "0", help="Requires integration with sent_tracker")

    st.markdown("---")

# Add Account Button
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("➕ Add New Account", use_container_width=True):
        st.session_state.show_account_form = True
        st.session_state.edit_account_id = None
        st.rerun()

# Display account form if needed
if st.session_state.show_account_form:
    st.markdown("---")

    # Get account data if editing
    account_data = None
    if st.session_state.edit_account_id:
        account_data = models.get_email_account(st.session_state.edit_account_id)

    # Display form
    form_result = email_account_form(account=account_data, verticals=verticals)

    if form_result is not None:
        # Form was submitted
        try:
            if st.session_state.edit_account_id:
                # Update existing account
                account_id = st.session_state.edit_account_id

                # Update account
                success = models.update_email_account(
                    account_id,
                    email_address=form_result['email_address'],
                    display_name=form_result['display_name'],
                    smtp_host=form_result['smtp_host'],
                    smtp_port=form_result['smtp_port'],
                    smtp_username=form_result['smtp_username'],
                    daily_send_limit=form_result['daily_send_limit'],
                    active=form_result['active']
                )

                # Update password if provided
                if form_result['password']:
                    models.update_email_account(account_id, password=form_result['password'])

                if success:
                    # Update vertical assignments
                    current_verticals = models.get_account_verticals(account_id)
                    new_verticals = form_result.get('verticals', [])

                    # Remove old assignments
                    for v_id in current_verticals:
                        if v_id not in new_verticals:
                            models.unassign_account_from_vertical(account_id, v_id)

                    # Add new assignments
                    for v_id in new_verticals:
                        if v_id not in current_verticals:
                            models.assign_account_to_vertical(account_id, v_id)

                    st.success("✅ Account updated successfully!")
                    st.session_state.show_account_form = False
                    st.session_state.edit_account_id = None
                    st.rerun()
                else:
                    st.error("Failed to update account.")

            else:
                # Create new account
                account_id = models.create_email_account(
                    email_address=form_result['email_address'],
                    smtp_host=form_result['smtp_host'],
                    smtp_port=form_result['smtp_port'],
                    smtp_username=form_result['smtp_username'],
                    password=form_result['password'],
                    daily_send_limit=form_result['daily_send_limit'],
                    display_name=form_result['display_name']
                )

                if account_id:
                    # Set active status
                    if not form_result['active']:
                        models.toggle_account_active(account_id, False)

                    # Add vertical assignments
                    for v_id in form_result.get('verticals', []):
                        models.assign_account_to_vertical(account_id, v_id)

                    st.success(f"✅ Account created successfully! (ID: {account_id})")
                    st.session_state.show_account_form = False
                    st.rerun()
                else:
                    st.error("Failed to create account. Email may already exist.")

        except Exception as e:
            st.error(f"Error saving account: {e}")

    # Cancel button
    if st.button("❌ Cancel"):
        st.session_state.show_account_form = False
        st.session_state.edit_account_id = None
        st.rerun()

    st.markdown("---")

# Display accounts
if accounts:
    st.subheader("Email Accounts")

    # Display accounts table
    accounts_table(accounts, show_actions=True)

    st.markdown("---")

    # Action buttons for each account
    st.subheader("Account Actions")

    for account in accounts:
        with st.expander(f"⚙️ {account['email_address']} - Actions"):
            col1, col2, col3, col4 = st.columns(4)

            account_id = account['account_id']

            with col1:
                if st.button(f"✏️ Edit", key=f"edit_{account_id}"):
                    st.session_state.show_account_form = True
                    st.session_state.edit_account_id = account_id
                    st.rerun()

            with col2:
                if st.button(f"🗑️ Delete", key=f"delete_{account_id}"):
                    if st.session_state.get(f'confirm_delete_{account_id}', False):
                        # Confirmed - delete account
                        success = models.delete_email_account(account_id)
                        if success:
                            st.success("Account deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete account.")
                    else:
                        # Show confirmation
                        st.session_state[f'confirm_delete_{account_id}'] = True
                        st.warning("⚠️ Click Delete again to confirm deletion.")

            with col3:
                # Toggle active status
                current_status = account.get('active', 0)
                new_status_label = "Deactivate" if current_status else "Activate"

                if st.button(f"🔄 {new_status_label}", key=f"toggle_{account_id}"):
                    success = models.toggle_account_active(account_id, not current_status)
                    if success:
                        st.success(f"Account {new_status_label.lower()}d!")
                        st.rerun()
                    else:
                        st.error("Failed to update status.")

            with col4:
                if st.button(f"🔌 Test SMTP", key=f"test_{account_id}"):
                    # Test SMTP connection
                    try:
                        is_valid, message = validators.validate_smtp_settings(
                            account['smtp_host'],
                            account['smtp_port'],
                            account['smtp_username'],
                            models.get_account_password_decrypted(account_id)
                        )

                        if is_valid:
                            st.success(f"✅ SMTP connection successful!")
                        else:
                            st.error(f"❌ SMTP connection failed: {message}")

                    except Exception as e:
                        st.error(f"Error testing connection: {e}")

    st.markdown("---")

    # Account-Vertical Assignment Matrix
    st.subheader("Account-Vertical Assignments")

    if verticals:
        # Get all assignments
        assignments = models.get_assignment_matrix()

        # Display matrix
        assignment_matrix(accounts, verticals, assignments)

        st.caption("Use the Edit button above to modify assignments for each account.")
    else:
        st.info("No verticals configured. Create verticals in the Verticals Manager.")

    st.markdown("---")

    # Capacity Summary
    st.subheader("Capacity Summary by Vertical")

    if verticals:
        capacity_data = []

        for vertical in verticals:
            vertical_id = vertical['vertical_id']
            vertical_accounts = models.get_vertical_accounts(vertical_id)

            total_capacity = sum(a.get('daily_send_limit', 0) for a in vertical_accounts if a.get('active'))
            account_count = len([a for a in vertical_accounts if a.get('active')])

            capacity_data.append({
                'Vertical': vertical['display_name'],
                'Accounts Assigned': account_count,
                'Daily Capacity': formatters.format_number(total_capacity)
            })

        if capacity_data:
            import pandas as pd
            df = pd.DataFrame(capacity_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No verticals configured.")

else:
    st.info("No email accounts configured yet.")
    st.markdown("""
    ### Getting Started

    Add your first email account to start sending campaigns:

    1. Click the "Add New Account" button above
    2. Enter your email and SMTP settings
    3. Set your daily sending limit
    4. Assign the account to one or more verticals

    **SMTP Settings:**
    - **Gmail:** smtp.gmail.com, port 587 (use app password)
    - **Outlook/Office365:** smtp.office365.com, port 587
    - **Yahoo:** smtp.mail.yahoo.com, port 587
    """)

# Refresh button
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
