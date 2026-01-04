"""
Page 2: Prospects Manager

Upload, view, and manage prospect lists for each vertical.
"""

import streamlit as st
import pandas as pd
from database import models
from integrations import (
    read_prospects,
    append_prospects,
    get_prospect_count,
    get_prospect_stats
)
from utils import validators, formatters
from components import prospects_table

# Page configuration
st.set_page_config(page_title="Prospects Manager", page_icon="📥", layout="wide")

st.title("📥 Prospects Manager")
st.markdown("Upload and manage prospect lists for your email campaigns.")
st.markdown("---")

# Get verticals
verticals = models.get_verticals(active_only=True)

if not verticals:
    st.warning("No active verticals found. Please create a vertical in the Verticals Manager first.")
    st.stop()

# Create tabs for Upload and View
tab1, tab2 = st.tabs(["📤 Upload Prospects", "👥 View Prospects"])

# TAB 1: Upload Prospects
with tab1:
    st.header("Upload Prospects")
    st.markdown("Upload CSV files to add prospects to your verticals. Files will be validated and deduplicated.")

    # Show upload zone for each vertical
    for vertical in verticals:
        with st.expander(f"📁 {vertical['display_name']} ({vertical['vertical_id']})", expanded=False):
            # Show current count
            try:
                current_count = get_prospect_count(vertical['vertical_id'])
                st.info(f"**Current prospects:** {formatters.format_number(current_count)}")
            except Exception as e:
                st.warning(f"Could not load prospect count: {e}")
                current_count = 0

            # File uploader
            uploaded_file = st.file_uploader(
                f"Upload CSV for {vertical['display_name']}",
                key=f"upload_{vertical['vertical_id']}",
                type=['csv'],
                help="CSV must contain columns: email, first_name, company_name, state, website"
            )

            if uploaded_file:
                try:
                    # Read uploaded file
                    df = pd.read_csv(uploaded_file)

                    # Show file info
                    st.write(f"**File:** {uploaded_file.name} ({len(df)} rows)")

                    # Validate
                    is_valid, error = validators.validate_prospect_csv(df)

                    if is_valid:
                        # Show preview
                        st.success("✅ CSV validation passed!")
                        st.write("**Preview (first 10 rows):**")
                        st.dataframe(df.head(10), use_container_width=True)

                        # Confirm button
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button(
                                f"✅ Add {len(df)} Prospects",
                                key=f"confirm_{vertical['vertical_id']}",
                                use_container_width=True
                            ):
                                try:
                                    with st.spinner("Adding prospects..."):
                                        count_added = append_prospects(vertical['vertical_id'], df)

                                    if count_added > 0:
                                        st.success(
                                            f"✅ Successfully added {formatters.format_number(count_added)} new prospects!"
                                        )
                                        new_total = current_count + count_added
                                        st.info(
                                            f"**Total prospects:** {formatters.format_number(new_total)}"
                                        )
                                        st.balloons()
                                    else:
                                        st.info("No new prospects added (all were duplicates).")

                                except Exception as e:
                                    st.error(f"Error adding prospects: {e}")

                        with col2:
                            st.caption("Duplicates will be automatically removed")

                    else:
                        st.error(f"❌ CSV validation failed: {error}")
                        st.write("**Required columns:** email, first_name, company_name, state, website")
                        st.write("**Your columns:**", list(df.columns))

                except Exception as e:
                    st.error(f"Error reading CSV file: {e}")

    st.markdown("---")
    st.markdown("""
    ### CSV Format Requirements
    Your CSV file must contain these columns:
    - **email**: Valid email address (required)
    - **first_name**: Prospect's first name (required)
    - **company_name**: Company name (required)
    - **state**: State abbreviation (required)
    - **website**: Company website (optional but recommended)

    Additional columns are allowed and will be preserved.
    """)

# TAB 2: View Prospects
with tab2:
    st.header("View Prospects")

    # Vertical selector
    vertical_options = [v['vertical_id'] for v in verticals]
    vertical_labels = [f"{v['display_name']} ({v['vertical_id']})" for v in verticals]

    selected_vertical = st.selectbox(
        "Select Vertical",
        options=vertical_options,
        format_func=lambda x: vertical_labels[vertical_options.index(x)],
        key='view_vertical'
    )

    # Get prospect stats
    try:
        stats = get_prospect_stats(selected_vertical)

        # Display stats
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total", formatters.format_number(stats.get('total', 0)))
        with col2:
            st.metric("Not Contacted", formatters.format_number(stats.get('not_contacted', 0)))
        with col3:
            st.metric("Initial Sent", formatters.format_number(stats.get('initial_sent', 0)))
        with col4:
            st.metric("Follow-up Sent", formatters.format_number(stats.get('followup_sent', 0)))
        with col5:
            st.metric("Responded", formatters.format_number(stats.get('responded', 0)))

    except Exception as e:
        st.error(f"Error loading prospect stats: {e}")

    st.markdown("---")

    # Read prospects
    try:
        df = read_prospects(selected_vertical)

        if not df.empty:
            # Search and filter
            col1, col2 = st.columns([3, 1])

            with col1:
                search = st.text_input(
                    "🔍 Search by email or company",
                    key='prospect_search',
                    placeholder="Type to search..."
                )

            with col2:
                # Status filter (if columns exist)
                status_filter = "All"
                if 'initial_sent' in df.columns or 'followup_sent' in df.columns:
                    status_filter = st.selectbox(
                        "Status Filter",
                        options=["All", "Not Contacted", "Initial Sent", "Follow-up Sent", "Responded"]
                    )

            # Apply search filter
            filtered_df = df.copy()

            if search:
                mask = (
                    filtered_df['email'].str.contains(search, case=False, na=False) |
                    filtered_df['company_name'].str.contains(search, case=False, na=False)
                )
                filtered_df = filtered_df[mask]

            # Apply status filter
            if status_filter != "All":
                if status_filter == "Not Contacted":
                    if 'initial_sent' in filtered_df.columns:
                        filtered_df = filtered_df[
                            (filtered_df['initial_sent'].isna()) |
                            (filtered_df['initial_sent'] == False) |
                            (filtered_df['initial_sent'] == 0)
                        ]
                elif status_filter == "Initial Sent":
                    if 'initial_sent' in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df['initial_sent'] == True]
                elif status_filter == "Follow-up Sent":
                    if 'followup_sent' in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df['followup_sent'] == True]
                elif status_filter == "Responded":
                    if 'responded' in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df['responded'] == True]

            # Display count
            st.write(f"**Showing {len(filtered_df):,} of {len(df):,} prospects**")

            # Display table
            prospects_table(filtered_df, editable=False, show_actions=True)

            st.markdown("---")

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                # Export button
                if st.button("📥 Export to CSV", use_container_width=True):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{selected_vertical}_prospects_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            with col2:
                # Refresh button
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()

            with col3:
                # Delete selected (placeholder - would need selection mechanism)
                st.button("🗑️ Delete Selected", use_container_width=True, disabled=True, help="Coming soon")

        else:
            st.info(f"No prospects found for **{selected_vertical}**. Upload a CSV file to get started.")

    except Exception as e:
        st.error(f"Error loading prospects: {e}")
        st.write("Make sure the vertical has a valid CSV file.")
