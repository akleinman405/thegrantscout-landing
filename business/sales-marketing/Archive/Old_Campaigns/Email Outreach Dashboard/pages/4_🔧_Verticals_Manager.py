"""
Page 4: Verticals Manager

Create and manage business verticals for email campaigns.
"""

import streamlit as st
import os
from database import models
from integrations import get_prospect_count
from utils import formatters
from components import vertical_form, verticals_table, vertical_card

# Page configuration
st.set_page_config(page_title="Verticals Manager", page_icon="🔧", layout="wide")

st.title("🔧 Verticals Manager")
st.markdown("Create and manage business verticals for your email campaigns.")
st.markdown("---")

# Get verticals
verticals = models.get_verticals(active_only=False)

# Session state for form display
if 'show_vertical_form' not in st.session_state:
    st.session_state.show_vertical_form = False
if 'edit_vertical_id' not in st.session_state:
    st.session_state.edit_vertical_id = None

# Summary metrics
if verticals:
    col1, col2, col3 = st.columns(3)

    active_count = sum(1 for v in verticals if v.get('active'))
    total_prospects = 0

    for v in verticals:
        try:
            count = get_prospect_count(v['vertical_id'])
            total_prospects += count
        except:
            pass

    with col1:
        st.metric("Total Verticals", len(verticals))
    with col2:
        st.metric("Active Verticals", active_count)
    with col3:
        st.metric("Total Prospects", formatters.format_number(total_prospects))

    st.markdown("---")

# Add Vertical Button
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("➕ Add New Vertical", use_container_width=True):
        st.session_state.show_vertical_form = True
        st.session_state.edit_vertical_id = None
        st.rerun()

# Display vertical form if needed
if st.session_state.show_vertical_form:
    st.markdown("---")

    # Get vertical data if editing
    vertical_data = None
    if st.session_state.edit_vertical_id:
        vertical_data = models.get_vertical(st.session_state.edit_vertical_id)

    # Display form
    form_result = vertical_form(vertical=vertical_data)

    if form_result is not None:
        # Form was submitted
        try:
            if st.session_state.edit_vertical_id:
                # Update existing vertical
                success = models.update_vertical(
                    st.session_state.edit_vertical_id,
                    display_name=form_result['display_name'],
                    target_industry=form_result['target_industry'],
                    csv_filename=form_result['csv_filename'],
                    active=form_result['active']
                )

                if success:
                    st.success("✅ Vertical updated successfully!")
                    st.session_state.show_vertical_form = False
                    st.session_state.edit_vertical_id = None
                    st.rerun()
                else:
                    st.error("Failed to update vertical.")

            else:
                # Create new vertical
                success = models.create_vertical(
                    vertical_id=form_result['vertical_id'],
                    display_name=form_result['display_name'],
                    target_industry=form_result['target_industry'],
                    csv_filename=form_result['csv_filename']
                )

                if success:
                    # Set active status if needed
                    if not form_result['active']:
                        models.toggle_vertical_active(form_result['vertical_id'], False)

                    # Create CSV file if it doesn't exist
                    from integrations.csv_handler import create_vertical_csv
                    try:
                        create_vertical_csv(form_result['vertical_id'])
                    except Exception as e:
                        st.warning(f"Vertical created but CSV file creation failed: {e}")

                    st.success(f"✅ Vertical '{form_result['display_name']}' created successfully!")
                    st.session_state.show_vertical_form = False
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create vertical. Vertical ID may already exist.")

        except Exception as e:
            st.error(f"Error saving vertical: {e}")

    # Cancel button
    if st.button("❌ Cancel"):
        st.session_state.show_vertical_form = False
        st.session_state.edit_vertical_id = None
        st.rerun()

    st.markdown("---")

# Display verticals
if verticals:
    st.subheader("Business Verticals")

    # Get prospect counts
    prospect_counts = {}
    for v in verticals:
        try:
            prospect_counts[v['vertical_id']] = get_prospect_count(v['vertical_id'])
        except:
            prospect_counts[v['vertical_id']] = 0

    # Display verticals table
    verticals_table(verticals, prospect_counts=prospect_counts, show_actions=True)

    st.markdown("---")

    # Display vertical cards in grid
    st.subheader("Vertical Details")

    cols = st.columns(min(3, len(verticals)))

    for idx, vertical in enumerate(verticals):
        with cols[idx % 3]:
            prospect_count = prospect_counts.get(vertical['vertical_id'], 0)
            vertical_card(vertical, prospect_count)

    st.markdown("---")

    # Action buttons for each vertical
    st.subheader("Vertical Actions")

    for vertical in verticals:
        with st.expander(f"⚙️ {vertical['display_name']} ({vertical['vertical_id']}) - Actions"):
            col1, col2, col3, col4 = st.columns(4)

            vertical_id = vertical['vertical_id']

            with col1:
                if st.button(f"✏️ Edit", key=f"edit_{vertical_id}"):
                    st.session_state.show_vertical_form = True
                    st.session_state.edit_vertical_id = vertical_id
                    st.rerun()

            with col2:
                if st.button(f"🗑️ Delete", key=f"delete_{vertical_id}"):
                    if st.session_state.get(f'confirm_delete_{vertical_id}', False):
                        # Confirmed - delete vertical
                        success = models.delete_vertical(vertical_id)
                        if success:
                            st.success("Vertical deleted! (Associated templates also removed)")
                            st.rerun()
                        else:
                            st.error("Failed to delete vertical.")
                    else:
                        # Show confirmation
                        st.session_state[f'confirm_delete_{vertical_id}'] = True
                        st.warning("⚠️ Click Delete again to confirm. This will also delete all templates!")

            with col3:
                # Toggle active status
                current_status = vertical.get('active', 0)
                new_status_label = "Deactivate" if current_status else "Activate"

                if st.button(f"🔄 {new_status_label}", key=f"toggle_{vertical_id}"):
                    success = models.toggle_vertical_active(vertical_id, not current_status)
                    if success:
                        st.success(f"Vertical {new_status_label.lower()}d!")
                        st.rerun()
                    else:
                        st.error("Failed to update status.")

            with col4:
                if st.button(f"📊 View Stats", key=f"stats_{vertical_id}"):
                    st.session_state[f'show_stats_{vertical_id}'] = not st.session_state.get(f'show_stats_{vertical_id}', False)

            # Show detailed stats if toggled
            if st.session_state.get(f'show_stats_{vertical_id}', False):
                st.markdown("---")
                st.markdown(f"### Statistics for {vertical['display_name']}")

                stats_col1, stats_col2, stats_col3 = st.columns(3)

                # Prospect stats
                try:
                    from integrations import get_prospect_stats
                    stats = get_prospect_stats(vertical_id)

                    with stats_col1:
                        st.markdown("**Prospects**")
                        st.write(f"Total: {formatters.format_number(stats.get('total', 0))}")
                        st.write(f"Not Contacted: {formatters.format_number(stats.get('not_contacted', 0))}")

                    with stats_col2:
                        st.markdown("**Outreach**")
                        st.write(f"Initial Sent: {formatters.format_number(stats.get('initial_sent', 0))}")
                        st.write(f"Follow-up Sent: {formatters.format_number(stats.get('followup_sent', 0))}")

                    with stats_col3:
                        st.markdown("**Engagement**")
                        st.write(f"Responded: {formatters.format_number(stats.get('responded', 0))}")
                        response_rate = stats.get('responded', 0) / stats.get('total', 1) if stats.get('total', 0) > 0 else 0
                        st.write(f"Response Rate: {formatters.format_percentage(response_rate)}")

                except Exception as e:
                    st.error(f"Error loading stats: {e}")

                # Template stats
                try:
                    templates = models.get_templates(vertical_id=vertical_id, active_only=False)
                    template_count = len(templates)
                    active_templates = len([t for t in templates if t.get('active')])

                    st.markdown(f"**Templates:** {active_templates} active / {template_count} total")
                except Exception as e:
                    st.error(f"Error loading templates: {e}")

                # Account assignments
                try:
                    assigned_accounts = models.get_vertical_accounts(vertical_id)
                    active_accounts = [a for a in assigned_accounts if a.get('active')]

                    st.markdown(f"**Email Accounts:** {len(active_accounts)} active assigned")

                    if active_accounts:
                        st.write("Assigned accounts:")
                        for account in active_accounts:
                            st.write(f"- {account.get('email_address')} ({account.get('daily_send_limit', 0)} daily limit)")
                except Exception as e:
                    st.error(f"Error loading accounts: {e}")

else:
    st.info("No verticals configured yet.")
    st.markdown("""
    ### Getting Started

    Create your first vertical to organize your email campaigns:

    1. Click "Add New Vertical" above
    2. Enter a unique Vertical ID (e.g., IDEA_078, debarment)
    3. Give it a descriptive display name
    4. Specify the target industry (optional)
    5. Save the vertical

    **What is a Vertical?**

    A vertical represents a specific business idea or market segment. For example:
    - **Debarment Monitor** - Alerts for federal contractor debarments
    - **Food Recall Alerts** - Notifications for restaurants about recalls
    - **Grant Alerts** - Grant opportunities for nonprofits

    Each vertical has its own:
    - Prospect list (CSV file)
    - Email templates
    - Campaign tracking
    - Analytics
    """)

# Refresh button
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
