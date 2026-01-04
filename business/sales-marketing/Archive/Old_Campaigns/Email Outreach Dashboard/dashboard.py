"""
Campaign Control Center - Main Dashboard Entry Point

This is the main Streamlit application file for the email campaign dashboard.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import os
import sys
from database import models, schema

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Welcome - Campaign Control Center",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Campaign Control Center v1.0 - Email Campaign Management Dashboard"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5em;
    }

    /* Subtitle styling */
    .subtitle {
        font-size: 1.2em;
        color: #666;
        text-align: center;
        margin-bottom: 2em;
    }

    /* Card styling */
    .info-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5em;
        margin: 1em 0;
        border-left: 4px solid #1f77b4;
    }

    /* Metric card enhancements */
    [data-testid="stMetricValue"] {
        font-size: 2em;
        font-weight: bold;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 5px;
        font-weight: 500;
    }

    /* Success/error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database on first run
@st.cache_resource
def initialize_app():
    """Initialize the application and database."""
    try:
        if not schema.database_exists():
            with st.spinner("Initializing database for first time..."):
                schema.initialize_database()
            return "initialized"
        return "exists"
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return "error"

# Run initialization
db_status = initialize_app()

if db_status == "initialized":
    st.success("✅ Database initialized successfully!")
    st.info("Welcome to Campaign Control Center! Get started by configuring your first email account and vertical.")

# Main page content
st.markdown('<div class="main-title">👋 Welcome to Campaign Control Center</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Email Campaign Management Dashboard</div>', unsafe_allow_html=True)

st.markdown("---")

# Welcome message and quick start guide
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Welcome!")

    st.markdown("""
    The **Campaign Control Center** is your centralized dashboard for managing multi-vertical email outreach campaigns.

    ### Features

    - **📊 Dashboard**: Real-time metrics and campaign performance analytics
    - **📥 Prospects Manager**: Upload and manage prospect lists via drag-and-drop CSV
    - **📧 Email Accounts**: Configure SMTP accounts with daily quotas and vertical assignments
    - **🔧 Verticals Manager**: Create and manage business verticals (market segments)
    - **✉️ Templates Manager**: Edit email templates with live preview
    - **📅 Campaign Planner**: View daily plans and weekly forecasts
    - **⚙️ Settings**: Global campaign settings and system configuration

    ### Navigation

    Use the **sidebar** to navigate between pages. Each page is designed for a specific aspect of campaign management.
    """)

with col2:
    st.header("Quick Start")

    # Get current state
    try:
        accounts = models.get_email_accounts(active_only=True)
        verticals = models.get_verticals(active_only=True)

        account_count = len(accounts)
        vertical_count = len(verticals)

        # Quick start checklist
        st.markdown("### Setup Progress")

        if account_count > 0:
            st.success(f"✅ {account_count} email account(s) configured")
        else:
            st.warning("⚠️ No email accounts yet")
            if st.button("→ Configure Email Accounts", key="goto_accounts"):
                st.switch_page("pages/3_📧_Email_Accounts.py")

        if vertical_count > 0:
            st.success(f"✅ {vertical_count} vertical(s) created")
        else:
            st.warning("⚠️ No verticals created yet")
            if st.button("→ Create Verticals", key="goto_verticals"):
                st.switch_page("pages/4_🔧_Verticals_Manager.py")

        # Check for prospects
        total_prospects = 0
        if verticals:
            from integrations import get_prospect_count
            for v in verticals:
                try:
                    total_prospects += get_prospect_count(v['vertical_id'])
                except:
                    pass

        if total_prospects > 0:
            st.success(f"✅ {total_prospects:,} prospects loaded")
        else:
            st.info("💡 Upload prospects to get started")

        # Check for templates
        template_count = 0
        if verticals:
            for v in verticals:
                templates = models.get_templates(vertical_id=v['vertical_id'], active_only=True)
                template_count += len(templates)

        if template_count > 0:
            st.success(f"✅ {template_count} template(s) created")
        else:
            st.info("💡 Create email templates")

    except Exception as e:
        st.error(f"Error loading status: {e}")

st.markdown("---")

# System Status
st.header("📡 System Status")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get counts
    all_accounts = models.get_email_accounts(active_only=False)
    all_verticals = models.get_verticals(active_only=False)

    active_accounts = len([a for a in all_accounts if a.get('active')])
    active_verticals = len([v for v in all_verticals if v.get('active')])

    # Get total capacity
    total_capacity = sum(a.get('daily_send_limit', 0) for a in all_accounts if a.get('active'))

    # Get sent today
    sent_today = 0
    try:
        from integrations import get_daily_metrics
        metrics = get_daily_metrics()
        sent_today = metrics.get('sent_today', 0)
    except:
        pass

    with col1:
        st.metric("Active Accounts", active_accounts)

    with col2:
        st.metric("Active Verticals", active_verticals)

    with col3:
        st.metric("Daily Capacity", f"{total_capacity:,}")

    with col4:
        st.metric("Sent Today", f"{sent_today:,}")

except Exception as e:
    st.error(f"Error loading system status: {e}")

st.markdown("---")

# Getting Started Guide
with st.expander("📖 Getting Started Guide", expanded=False):
    st.markdown("""
    ### Step-by-Step Setup

    #### 1. Configure Email Accounts
    Navigate to **📧 Email Accounts** and add your first email account:
    - Enter email address and SMTP settings
    - Set daily sending limit (e.g., 450 emails/day)
    - Test SMTP connection to verify settings

    #### 2. Create Verticals
    Go to **🔧 Verticals Manager** and create your first vertical:
    - Choose a unique Vertical ID (e.g., `debarment`, `food_recall`)
    - Give it a descriptive display name
    - Specify target industry

    #### 3. Upload Prospects
    In **📥 Prospects Manager**, upload your prospect CSV files:
    - Drag and drop CSV files for each vertical
    - Files must contain: email, first_name, company_name, state, website
    - Duplicates are automatically removed

    #### 4. Create Email Templates
    Visit **✉️ Templates Manager** to create email templates:
    - Create both Initial and Follow-up templates for each vertical
    - Use template variables like `{first_name}`, `{company_name}`
    - Preview templates before saving

    #### 5. Assign Accounts to Verticals
    Back in **📧 Email Accounts**, assign accounts to verticals:
    - Each account can serve multiple verticals
    - Load balancing is automatic

    #### 6. Monitor Campaign
    Use **📊 Dashboard** to monitor your campaigns:
    - View real-time metrics and charts
    - Track response rates
    - Monitor email account quota usage

    #### 7. Plan Ahead
    Check **📅 Campaign Planner** for forecasts:
    - See today's sending plan
    - View 7-day forecast
    - Use capacity calculator for planning

    ### Integration with Email Scripts

    This dashboard integrates seamlessly with your existing Python email automation scripts:
    - Dashboard reads `sent_tracker.csv` for metrics
    - Templates sync with script configuration
    - Prospect uploads are immediately available to scripts
    - Coordination happens via `coordination.json`

    ### Need Help?

    - Check **⚙️ Settings** for troubleshooting resources
    - Review `SETUP_INSTRUCTIONS.md` for detailed setup
    - See `TROUBLESHOOTING.md` for common issues
    """)

# Recent Activity (placeholder for future enhancement)
with st.expander("📋 Recent Activity", expanded=False):
    st.info("Recent activity tracking coming soon. This will show recent uploads, template changes, and campaign events.")

# Footer
st.markdown("---")
st.caption("Campaign Control Center v1.0 | Built with Streamlit | © 2025")

# Debug info (only in development)
if st.checkbox("Show Debug Info", value=False):
    st.markdown("### Debug Information")

    st.write("**Python Version:**", sys.version)
    st.write("**Working Directory:**", os.getcwd())

    try:
        from utils import windows_paths
        st.write("**Base Directory:**", windows_paths.get_base_dir())
        st.write("**Database Path:**", windows_paths.get_database_path())
    except Exception as e:
        st.error(f"Error loading paths: {e}")

    st.write("**Session State:**", st.session_state)
