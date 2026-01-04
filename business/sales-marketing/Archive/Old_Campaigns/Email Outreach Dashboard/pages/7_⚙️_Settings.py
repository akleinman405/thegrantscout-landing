"""
Page 7: Settings

Global campaign settings, file paths, and system information.
"""

import streamlit as st
import os
from datetime import datetime
from database import models
from utils import formatters, windows_paths
from components import settings_form

# Page configuration
st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings")
st.markdown("Configure global campaign settings and view system information.")
st.markdown("---")

# Get current settings
current_settings = models.get_all_settings()

# GLOBAL CAMPAIGN SETTINGS
st.header("🌍 Global Campaign Settings")

# Display and edit settings
form_result = settings_form(current_settings)

if form_result is not None:
    # Save settings
    try:
        for key, value in form_result.items():
            models.set_setting(key, value)

        st.success("✅ Settings saved successfully!")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Error saving settings: {e}")

st.markdown("---")

# FILE PATHS
st.header("📁 File Paths")

st.markdown("These paths are used by the dashboard and email automation scripts.")

try:
    paths_data = {
        'Base Directory': windows_paths.get_base_dir(),
        'Database Path': windows_paths.get_database_path(),
        'Sent Tracker': windows_paths.get_sent_tracker_path(),
        'Response Tracker': windows_paths.get_response_tracker_path(),
        'Coordination File': windows_paths.get_coordination_path(),
        'Error Log': windows_paths.get_error_log_path(),
    }

    for label, path in paths_data.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{label}:**")
        with col2:
            st.code(path, language=None)

            # Check if file exists
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                st.caption(f"✅ Exists ({formatters.format_file_size(file_size)})")
            else:
                st.caption("⚠️ File not found")

except Exception as e:
    st.error(f"Error loading file paths: {e}")

st.markdown("---")

# DATA MANAGEMENT
st.header("💾 Data Management")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Export Data")
    if st.button("📥 Export All Data", use_container_width=True, help="Export database and settings to ZIP"):
        st.info("Export functionality coming soon.")

with col2:
    st.subheader("Import Data")
    if st.button("📤 Import Data", disabled=True, use_container_width=True, help="Import from ZIP"):
        st.info("Import functionality coming soon.")

with col3:
    st.subheader("Reset")
    if st.button("🔄 Reset Daily Counters", disabled=True, use_container_width=True, help="Reset daily sent counts"):
        st.info("Reset functionality coming soon.")

st.markdown("---")

# SYSTEM INFORMATION
st.header("ℹ️ System Information")

try:
    # Get database stats
    verticals = models.get_verticals(active_only=False)
    accounts = models.get_email_accounts(active_only=False)
    all_templates = []

    for vertical in verticals:
        templates = models.get_templates(vertical_id=vertical['vertical_id'], active_only=False)
        all_templates.extend(templates)

    # Get database size
    db_path = windows_paths.get_database_path()
    db_size = 0
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)

    # Get total prospects
    total_prospects = 0
    for vertical in verticals:
        try:
            from integrations import get_prospect_count
            total_prospects += get_prospect_count(vertical['vertical_id'])
        except:
            pass

    # Get total sent emails
    total_sent = 0
    try:
        from integrations import read_sent_tracker
        sent_df = read_sent_tracker()
        total_sent = len(sent_df) if not sent_df.empty else 0
    except:
        pass

    # Display system info
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Database Statistics")
        st.write(f"**Database Size:** {formatters.format_file_size(db_size)}")
        st.write(f"**Verticals:** {len(verticals)}")
        st.write(f"**Email Accounts:** {len(accounts)}")
        st.write(f"**Templates:** {len(all_templates)}")

    with col2:
        st.markdown("### Campaign Statistics")
        st.write(f"**Total Prospects:** {formatters.format_number(total_prospects)}")
        st.write(f"**Total Emails Sent:** {formatters.format_number(total_sent)}")
        st.write(f"**Dashboard Version:** 1.0.0")
        st.write(f"**Last Accessed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    st.error(f"Error loading system information: {e}")

st.markdown("---")

# TROUBLESHOOTING
st.header("🔧 Troubleshooting")

with st.expander("🐛 Common Issues"):
    st.markdown("""
    ### Dashboard Issues

    **Dashboard won't start:**
    - Check that all dependencies are installed: `pip install -r requirements.txt`
    - Ensure you're in the correct directory
    - Check Python version (3.9+ required)

    **Data not showing:**
    - Verify file paths above point to correct locations
    - Check that CSV files exist and are readable
    - Try clicking "Refresh Data" button

    **Database errors:**
    - Check database file permissions
    - Ensure database isn't corrupted
    - Check disk space

    **SMTP connection failures:**
    - Verify SMTP settings are correct
    - Check internet connection
    - For Gmail, use app-specific password
    - Check firewall settings

    ### Integration Issues

    **Email scripts can't find data:**
    - Verify file paths match between dashboard and scripts
    - Check CSV file permissions
    - Ensure vertical IDs match exactly

    **Templates not updating:**
    - Check template file permissions
    - Verify template files are in correct location
    - Clear cache and refresh

    ### Need More Help?

    Check the detailed troubleshooting guide in `TROUBLESHOOTING.md`
    """)

with st.expander("📚 Resources"):
    st.markdown("""
    ### Documentation

    - **Setup Instructions:** See `SETUP_INSTRUCTIONS.md`
    - **Integration Guide:** See `INTEGRATION_API_GUIDE.md`
    - **Database Documentation:** See `DATABASE_IMPLEMENTATION_SUMMARY.md`
    - **Backend Documentation:** See `BACKEND_INTEGRATION_SUMMARY.md`

    ### Support

    - Review the README.md for project overview
    - Check implementation_docs folder for technical details
    - Test integration with `test_integration.py`
    """)

with st.expander("⌨️ Keyboard Shortcuts"):
    st.markdown("""
    ### Streamlit Shortcuts

    - **R** - Refresh/rerun the app
    - **C** - Clear cache
    - **S** - Show settings
    - **K** - Open command palette (if available)

    ### Navigation

    Use the sidebar to navigate between pages.
    """)

# Refresh button
st.markdown("---")
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Clear cache button
if st.button("🗑️ Clear All Cache", use_container_width=True):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Cache cleared!")
    st.rerun()
