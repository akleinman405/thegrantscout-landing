"""
Page 8: Campaign Control

Start/stop campaigns, monitor real-time email sending, and send test emails.
"""

import streamlit as st
import subprocess
import os
import pandas as pd
from datetime import datetime
import time
from pathlib import Path
from database import models
from integrations import read_sent_tracker
from utils import windows_paths, formatters, validators
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page configuration
st.set_page_config(page_title="Campaign Control", page_icon="🚀", layout="wide")

st.title("🚀 Campaign Control")
st.markdown("Start campaigns, monitor real-time email sending, and run test emails.")
st.markdown("---")

# Initialize session state
if 'campaign_process' not in st.session_state:
    st.session_state.campaign_process = None
if 'campaign_running' not in st.session_state:
    st.session_state.campaign_running = False
if 'last_email_count' not in st.session_state:
    st.session_state.last_email_count = 0

# Path to email scripts
SCRIPT_DIR = Path(r"C:\Business Factory (Research) 11-1-2025\06_GO_TO_MARKET\outreach_sequences\Email Campaign 2025-11-3")

# ============================================================================
# TAB 1: CAMPAIGN CONTROL
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📊 Campaign Control", "📡 Live Feed", "🧪 Test Emails"])

with tab1:
    st.header("Campaign Management")

    # Campaign Status
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.campaign_running:
            st.success("🟢 Campaign Running")
        else:
            st.info("⚫ Campaign Stopped")

    with col2:
        # Get today's sent count
        sent_df = read_sent_tracker()
        if not sent_df.empty:
            today = datetime.now().date()
            if 'timestamp' in sent_df.columns:
                sent_df['date'] = pd.to_datetime(sent_df['timestamp']).dt.date
                today_count = len(sent_df[sent_df['date'] == today])
                st.metric("Sent Today", formatters.format_number(today_count))
            else:
                st.metric("Sent Today", "0")
        else:
            st.metric("Sent Today", "0")

    with col3:
        # Check if in business hours
        now = datetime.now()
        is_business_hours = (
            now.weekday() < 5 and  # Monday-Friday
            9 <= now.hour < 15      # 9am-3pm
        )
        if is_business_hours:
            st.success("✅ Business Hours")
        else:
            st.warning("⏰ Outside Business Hours")

    st.markdown("---")

    # Campaign Controls
    st.subheader("Campaign Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Start Campaign")

        # Campaign type selection
        campaign_type = st.selectbox(
            "Campaign Type",
            options=['initial', 'followup', 'both'],
            format_func=lambda x: {
                'initial': 'Initial Outreach Only',
                'followup': 'Follow-up Only',
                'both': 'Both (Initial + Follow-up)'
            }[x]
        )

        # Vertical selection
        verticals = models.get_verticals(active_only=True)
        if verticals:
            vertical_options = ['all'] + [v['vertical_id'] for v in verticals]
            selected_vertical = st.selectbox(
                "Target Vertical",
                options=vertical_options,
                format_func=lambda x: "All Verticals" if x == 'all' else x
            )
        else:
            st.warning("No verticals configured. Go to Verticals Manager to add verticals.")
            selected_vertical = None

        # Daily limit override
        use_limit = st.checkbox("Override Daily Limit", value=False)
        if use_limit:
            daily_limit = st.number_input(
                "Max Emails Today",
                min_value=1,
                max_value=1000,
                value=100,
                step=10
            )
        else:
            daily_limit = None

        # Start button
        if st.button("▶️ Start Campaign", type="primary", disabled=st.session_state.campaign_running):
            st.warning("⚠️ **Campaign starting feature is for demonstration.**")
            st.info("""
            To actually run campaigns:
            1. Open a separate terminal/command prompt
            2. Navigate to: `Email Campaign 2025-11-3`
            3. Run: `python send_initial_outreach.py` or `python send_followup.py`

            The dashboard will automatically detect and display sent emails in the Live Feed.
            """)

            st.session_state.campaign_running = True
            st.success("✅ Campaign mode activated! Run scripts manually in terminal.")

    with col2:
        st.markdown("### Stop Campaign")
        st.info("""
        **To stop running campaigns:**

        1. Go to the terminal where the script is running
        2. Press `Ctrl + C`
        3. The script will gracefully shutdown and save progress

        Check the Live Feed to monitor when emails stop sending.
        """)

        if st.button("⏹️ Mark as Stopped", disabled=not st.session_state.campaign_running):
            st.session_state.campaign_running = False
            st.success("✅ Campaign marked as stopped.")

    st.markdown("---")

    # Quick Instructions
    with st.expander("📖 How to Run Campaigns Manually"):
        st.markdown(f"""
        ### Running Email Campaigns

        **Location:** `{SCRIPT_DIR}`

        #### Initial Outreach Campaign
        ```bash
        cd "{SCRIPT_DIR}"
        python send_initial_outreach.py
        ```

        #### Follow-up Campaign
        ```bash
        cd "{SCRIPT_DIR}"
        python send_followup.py
        ```

        #### Features:
        - ✅ Respects business hours (9am-3pm EST, Mon-Fri)
        - ✅ Smart pacing with random delays
        - ✅ Automatic coordination (splits capacity between initial/followup)
        - ✅ Graceful shutdown on Ctrl+C
        - ✅ Progress tracking in sent_tracker.csv

        #### Monitoring:
        - Use the **Live Feed** tab to watch emails being sent in real-time
        - Check the **Dashboard** page for metrics and analytics
        - View sent_tracker.csv for detailed logs
        """)

# ============================================================================
# TAB 2: LIVE EMAIL FEED
# ============================================================================

with tab2:
    st.header("📡 Real-Time Email Feed")
    st.caption("Auto-refreshes every 5 seconds to show newly sent emails")

    # Auto-refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        auto_refresh = st.checkbox("🔄 Auto-Refresh (5 seconds)", value=True)

    with col2:
        if st.button("🔃 Refresh Now"):
            st.rerun()

    with col3:
        show_count = st.number_input("Show Last N Emails", min_value=10, max_value=500, value=50, step=10)

    st.markdown("---")

    # Read sent tracker
    try:
        sent_df = read_sent_tracker()

        # Debug info
        st.caption(f"Debug: Loaded {len(sent_df)} rows from sent_tracker.csv")

        if not sent_df.empty:
            # Sort by timestamp descending (newest first)
            if 'timestamp' in sent_df.columns:
                sent_df = sent_df.sort_values('timestamp', ascending=False)

            # Take last N emails
            recent_df = sent_df.head(show_count)

            # Display count
            st.info(f"📊 Showing {len(recent_df)} most recent emails (Total sent: {len(sent_df):,})")

            # Format for display
            display_df = recent_df.copy()

            if 'timestamp' in display_df.columns:
                # Format timestamp
                display_df['Time'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Select and rename columns for clean display
            display_columns = {
                'Time': 'Time',
                'email': 'Recipient',
                'vertical': 'Vertical',
                'message_type': 'Type',
                'subject_line': 'Subject',
                'status': 'Status'
            }

            # Filter to available columns
            available_cols = [col for col in display_columns.keys() if col in display_df.columns or col == 'Time']

            # Check which columns are actually available
            required_cols = ['email', 'vertical', 'message_type', 'subject_line', 'status']
            missing_cols = [col for col in required_cols if col not in display_df.columns]

            if missing_cols:
                st.warning(f"⚠️ Some columns are missing from sent_tracker.csv: {', '.join(missing_cols)}")
                st.dataframe(display_df, height=600)
            elif 'Time' in available_cols and 'email' in display_df.columns:
                show_df = display_df[['Time', 'email', 'vertical', 'message_type', 'subject_line', 'status']].copy()
                show_df.columns = ['Time', 'Recipient', 'Vertical', 'Type', 'Subject', 'Status']

                # Style the dataframe
                def highlight_status(val):
                    if val == 'SUCCESS':
                        return 'background-color: #d4edda; color: #155724'
                    elif val == 'ERROR':
                        return 'background-color: #f8d7da; color: #721c24'
                    else:
                        return ''

                styled_df = show_df.style.map(highlight_status, subset=['Status'])

                st.dataframe(styled_df, width=None, height=600)

                # Summary stats
                col1, col2, col3 = st.columns(3)

                with col1:
                    success_count = len(recent_df[recent_df['status'] == 'SUCCESS'])
                    st.metric("✅ Successful", success_count)

                with col2:
                    error_count = len(recent_df[recent_df['status'] == 'ERROR'])
                    st.metric("❌ Errors", error_count)

                with col3:
                    if success_count + error_count > 0:
                        success_rate = (success_count / (success_count + error_count)) * 100
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    else:
                        st.metric("Success Rate", "N/A")
            else:
                st.dataframe(display_df, width=None, height=600)
        else:
            st.info("📭 No emails sent yet. Start a campaign to see emails appear here in real-time!")

    except Exception as e:
        st.error(f"Error loading email feed: {e}")

    # Auto-refresh implementation
    if auto_refresh:
        try:
            time.sleep(5)
            st.rerun()
        except Exception as e:
            st.error(f"Auto-refresh error: {e}")

# ============================================================================
# TAB 3: TEST EMAILS
# ============================================================================

with tab3:
    st.header("🧪 Test Email Tool")
    st.info("Send test emails to verify templates and SMTP settings before running campaigns.")

    # Check prerequisites BEFORE showing form
    accounts = models.get_email_accounts(active_only=True)
    verticals = models.get_verticals(active_only=True)

    if not accounts:
        st.error("❌ No email accounts configured! Go to Email Accounts page to add an account.")

    if not verticals:
        st.error("❌ No verticals configured! Go to Verticals Manager to add verticals.")

    # Only show form if prerequisites are met
    if accounts and verticals:
        # Test email form
        with st.form("test_email_form"):
            st.subheader("Test Email Configuration")

            col1, col2 = st.columns(2)

            with col1:
                # Email account selection
                account_options = {
                    f"{acc['email_address']} ({acc['display_name']})": acc['account_id']
                    for acc in accounts
                }

                selected_account_display = st.selectbox(
                    "From Email Account",
                    options=list(account_options.keys())
                )
                selected_account_id = account_options[selected_account_display]
                selected_account = next(acc for acc in accounts if acc['account_id'] == selected_account_id)

                # Vertical selection
                vertical_options = {
                    f"{v['display_name']} ({v['vertical_id']})": v['vertical_id']
                    for v in verticals
                }

                selected_vertical_display = st.selectbox(
                    "Vertical / Template",
                    options=list(vertical_options.keys())
                )
                selected_vertical_id = vertical_options[selected_vertical_display]

        with col2:
            # Test email address
            test_email = st.text_input(
                "Test Email Address",
                placeholder="your.email@example.com",
                help="Enter your own email address to receive the test"
            )

            # Message type
            message_type = st.selectbox(
                "Message Type",
                options=['initial', 'followup'],
                format_func=lambda x: x.title()
            )

        # Test data
        st.markdown("### Test Prospect Data")
        st.caption("This data will be used to fill in template variables like {first_name}, {company}, etc.")

        col1, col2 = st.columns(2)

        with col1:
            test_first_name = st.text_input("First Name", value="John")
            test_company = st.text_input("Company Name", value="Test Company Inc.")

        with col2:
            test_state = st.text_input("State", value="CA")
            test_website = st.text_input("Website", value="www.example.com")

            # Submit button
            submitted = st.form_submit_button("📧 Send Test Email", type="primary")

        # Handle form submission
        if submitted:
            # Validate inputs
            if not test_email or not validators.validate_email(test_email)[0]:
                st.error("❌ Please enter a valid test email address.")
            else:
                try:
                    # Get template
                    templates = models.get_templates(
                        vertical_id=selected_vertical_id,
                        template_type=message_type,
                        active_only=True
                    )

                    if not templates:
                        st.error(f"❌ No {message_type} template found for {selected_vertical_id}. Create one in Templates Manager.")
                    else:
                        template = templates[0]  # Use first active template

                        # Prepare template variables
                        template_vars = {
                            'first_name': test_first_name,
                            'company': test_company,
                            'company_name': test_company,
                            'state': test_state,
                            'website': test_website,
                            'greeting': f"Hello {test_first_name}",
                        }

                        # Format template
                        try:
                            subject = template['subject_line'].format(**template_vars)
                            body = template['email_body'].format(**template_vars)
                        except KeyError as e:
                            st.error(f"❌ Template has undefined variable: {e}")
                            st.stop()

                        # Create email message
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = f"[TEST] {subject}"
                        msg['From'] = selected_account['email_address']
                        msg['To'] = test_email

                        # Add body
                        text_part = MIMEText(body, 'plain')
                        msg.attach(text_part)

                        # Show preview
                        st.success("✅ Test email prepared!")

                        with st.expander("📧 Email Preview", expanded=True):
                            st.markdown(f"**From:** {selected_account['email_address']}")
                            st.markdown(f"**To:** {test_email}")
                            st.markdown(f"**Subject:** [TEST] {subject}")
                            st.markdown("**Body:**")
                            st.text(body)

                        # Send email
                        with st.spinner("Sending test email..."):
                            try:
                                # Decrypt password
                                from database.encryption import decrypt_password
                                password = decrypt_password(selected_account['password_encrypted'])

                                # Connect to SMTP
                                server = smtplib.SMTP(
                                    selected_account['smtp_host'],
                                    selected_account['smtp_port']
                                )
                                server.starttls()
                                server.login(selected_account['smtp_username'], password)

                                # Send email
                                server.send_message(msg)
                                server.quit()

                                st.success(f"""
                                ✅ **Test email sent successfully!**

                                - **To:** {test_email}
                                - **From:** {selected_account['email_address']}
                                - **Template:** {template['template_name']} ({message_type})
                                - **Vertical:** {selected_vertical_id}

                                Check your inbox at {test_email}
                                """)

                            except smtplib.SMTPAuthenticationError:
                                st.error(f"""
                                ❌ **SMTP Authentication Failed**

                                The email credentials for {selected_account['email_address']} are incorrect.
                                Go to Email Accounts page and update the password.
                                """)
                            except smtplib.SMTPException as e:
                                st.error(f"""
                                ❌ **SMTP Error**

                                {str(e)}

                                Check SMTP settings for {selected_account['email_address']}
                                """)
                            except Exception as e:
                                st.error(f"❌ Error sending test email: {str(e)}")

                except Exception as e:
                    st.error(f"❌ Error preparing test email: {str(e)}")

    # Test history
    st.markdown("---")
    with st.expander("📋 Test Email Tips"):
        st.markdown("""
        ### Best Practices for Test Emails

        ✅ **Before Running Campaigns:**
        1. Send test emails to yourself for each vertical
        2. Verify template variables populate correctly
        3. Check subject lines aren't too spammy
        4. Ensure unsubscribe links work (if applicable)
        5. Test from each email account you'll use

        ✅ **What to Check:**
        - Email formatting looks professional
        - All variables replaced (no {first_name} showing)
        - Links work correctly
        - Sender name displays properly
        - Email doesn't land in spam

        ✅ **Common Issues:**
        - Missing template variables: Add them in Templates Manager
        - SMTP errors: Check password and settings in Email Accounts
        - Spam folder: Adjust subject line, avoid spam trigger words
        """)
