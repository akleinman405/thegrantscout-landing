"""
Page 5: Templates Manager

Create and edit email templates for each vertical.
"""

import streamlit as st
from database import models
from components import template_editor_form, templates_table

# Page configuration
st.set_page_config(page_title="Templates Manager", page_icon="✉️", layout="wide")

st.title("✉️ Templates Manager")
st.markdown("Create and edit email templates for your campaigns.")
st.markdown("---")

# Get verticals
verticals = models.get_verticals(active_only=True)

if not verticals:
    st.warning("No active verticals found. Please create a vertical in the Verticals Manager first.")
    st.stop()

# Session state for form display
if 'show_template_form' not in st.session_state:
    st.session_state.show_template_form = False
if 'edit_template_id' not in st.session_state:
    st.session_state.edit_template_id = None
if 'selected_vertical' not in st.session_state:
    st.session_state.selected_vertical = verticals[0]['vertical_id']

# Vertical selector using tabs
vertical_names = [f"{v['display_name']}" for v in verticals]
vertical_ids = [v['vertical_id'] for v in verticals]

# Create tabs for each vertical
tabs = st.tabs(vertical_names)

for idx, (tab, vertical) in enumerate(zip(tabs, verticals)):
    with tab:
        vertical_id = vertical['vertical_id']

        # Get templates for this vertical
        templates = models.get_templates(vertical_id=vertical_id, active_only=False)

        # Template stats
        col1, col2, col3, col4 = st.columns(4)

        initial_templates = [t for t in templates if t.get('template_type') == 'initial']
        followup_templates = [t for t in templates if t.get('template_type') == 'followup']
        active_templates = [t for t in templates if t.get('active')]

        with col1:
            st.metric("Total Templates", len(templates))
        with col2:
            st.metric("Initial Templates", len(initial_templates))
        with col3:
            st.metric("Follow-up Templates", len(followup_templates))
        with col4:
            st.metric("Active Templates", len(active_templates))

        st.markdown("---")

        # Add template button
        if st.button(f"➕ Add Template for {vertical['display_name']}", key=f"add_{vertical_id}"):
            st.session_state.show_template_form = True
            st.session_state.edit_template_id = None
            st.session_state.selected_vertical = vertical_id
            st.rerun()

        # Display templates
        if templates:
            st.subheader(f"Templates for {vertical['display_name']}")

            # Separate by type
            st.markdown("#### Initial Outreach Templates")
            if initial_templates:
                templates_table(initial_templates, show_actions=True)
            else:
                st.info("No initial templates created yet.")

            st.markdown("---")

            st.markdown("#### Follow-up Templates")
            if followup_templates:
                templates_table(followup_templates, show_actions=True)
            else:
                st.info("No follow-up templates created yet.")

            st.markdown("---")

            # Action buttons for each template
            st.subheader("Template Actions")

            for template in templates:
                template_id = template['template_id']
                template_name = template['template_name']
                template_type = template['template_type'].title()

                with st.expander(f"⚙️ {template_name} ({template_type}) - Actions"):
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{template_id}"):
                            st.session_state.show_template_form = True
                            st.session_state.edit_template_id = template_id
                            st.session_state.selected_vertical = vertical_id
                            st.rerun()

                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{template_id}"):
                            if st.session_state.get(f'confirm_delete_{template_id}', False):
                                # Confirmed - delete template
                                success = models.delete_template(template_id)
                                if success:
                                    st.success("Template deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete template.")
                            else:
                                # Show confirmation
                                st.session_state[f'confirm_delete_{template_id}'] = True
                                st.warning("⚠️ Click Delete again to confirm deletion.")

                    with col3:
                        # Toggle active status
                        current_status = template.get('active', 0)
                        new_status_label = "Deactivate" if current_status else "Activate"

                        if st.button(f"🔄 {new_status_label}", key=f"toggle_{template_id}"):
                            success = models.toggle_template_active(template_id, not current_status)
                            if success:
                                st.success(f"Template {new_status_label.lower()}d!")
                                st.rerun()
                            else:
                                st.error("Failed to update status.")

                    with col4:
                        if st.button(f"📋 Duplicate", key=f"duplicate_{template_id}"):
                            # Duplicate template
                            try:
                                new_id = models.create_template(
                                    vertical_id=template['vertical_id'],
                                    template_type=template['template_type'],
                                    template_name=f"{template['template_name']} (Copy)",
                                    subject_line=template['subject_line'],
                                    email_body=template['email_body']
                                )

                                if new_id:
                                    st.success("Template duplicated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to duplicate template.")
                            except Exception as e:
                                st.error(f"Error duplicating template: {e}")

                    # Show template preview
                    if st.session_state.get(f'show_preview_{template_id}', False):
                        st.markdown("---")
                        st.markdown("### Template Preview")

                        st.text(f"Subject: {template['subject_line']}")
                        st.text_area("Body", template['email_body'], height=200, disabled=True, key=f"preview_{template_id}")

                    if st.button("👁️ Toggle Preview", key=f"preview_btn_{template_id}"):
                        st.session_state[f'show_preview_{template_id}'] = not st.session_state.get(f'show_preview_{template_id}', False)
                        st.rerun()

        else:
            st.info(f"No templates created for {vertical['display_name']} yet.")
            st.markdown("""
            ### Create Your First Template

            Templates are used by the email automation scripts to send personalized emails.

            **Template Types:**
            - **Initial**: First contact with prospects
            - **Follow-up**: Follow-up email sent after initial

            **Available Variables:**
            - `{greeting}` - Personalized greeting (e.g., " John" or "")
            - `{first_name}` - Prospect's first name
            - `{company_name}` - Company name
            - `{state}` - State abbreviation
            - `{website}` - Company website

            Click "Add Template" above to get started!
            """)

# Display template editor form if needed
if st.session_state.show_template_form:
    st.markdown("---")
    st.markdown("---")

    # Get template data if editing
    template_data = None
    if st.session_state.edit_template_id:
        template_data = models.get_template(st.session_state.edit_template_id)

    # Display form
    form_result = template_editor_form(
        template=template_data,
        vertical_id=st.session_state.selected_vertical
    )

    if form_result is not None:
        # Form was submitted
        try:
            if st.session_state.edit_template_id:
                # Update existing template
                success = models.update_template(
                    st.session_state.edit_template_id,
                    template_name=form_result['template_name'],
                    template_type=form_result['template_type'],
                    subject_line=form_result['subject_line'],
                    email_body=form_result['email_body']
                )

                if success:
                    st.success("✅ Template updated successfully!")

                    # Also update template file
                    try:
                        from integrations.template_manager import save_template_to_file
                        save_template_to_file(
                            vertical_id=form_result['vertical_id'],
                            template_type=form_result['template_type'],
                            template_name=form_result['template_name'],
                            subject_line=form_result['subject_line'],
                            email_body=form_result['email_body']
                        )
                        st.info("Template file updated for email scripts.")
                    except Exception as e:
                        st.warning(f"Template saved to database but file update failed: {e}")

                    st.session_state.show_template_form = False
                    st.session_state.edit_template_id = None
                    st.rerun()
                else:
                    st.error("Failed to update template.")

            else:
                # Create new template
                template_id = models.create_template(
                    vertical_id=form_result['vertical_id'],
                    template_type=form_result['template_type'],
                    template_name=form_result['template_name'],
                    subject_line=form_result['subject_line'],
                    email_body=form_result['email_body']
                )

                if template_id:
                    st.success(f"✅ Template created successfully! (ID: {template_id})")

                    # Also create template file
                    try:
                        from integrations.template_manager import save_template_to_file
                        save_template_to_file(
                            vertical_id=form_result['vertical_id'],
                            template_type=form_result['template_type'],
                            template_name=form_result['template_name'],
                            subject_line=form_result['subject_line'],
                            email_body=form_result['email_body']
                        )
                        st.info("Template file created for email scripts.")
                    except Exception as e:
                        st.warning(f"Template saved to database but file creation failed: {e}")

                    st.session_state.show_template_form = False
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create template.")

        except Exception as e:
            st.error(f"Error saving template: {e}")

    # Cancel button
    if st.button("❌ Cancel Template Editor"):
        st.session_state.show_template_form = False
        st.session_state.edit_template_id = None
        st.rerun()

# Sync button
st.markdown("---")
st.subheader("📁 Sync Templates to Files")
st.info("""
**Important:** Email scripts read templates from files, not the database.

After editing templates in this dashboard, click the button below to sync them to files.
This ensures your email scripts use the updated templates.
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Sync All Templates to Files", use_container_width=True, type="primary"):
        from integrations import sync_templates_from_db

        verticals = models.get_verticals(active_only=True)

        if not verticals:
            st.warning("No verticals found to sync.")
        else:
            success_count = 0
            error_count = 0

            with st.spinner("Syncing templates..."):
                for vertical in verticals:
                    try:
                        synced = sync_templates_from_db(vertical['vertical_id'])
                        success_count += len(synced)
                    except Exception as e:
                        st.warning(f"Error syncing {vertical['vertical_id']}: {e}")
                        error_count += 1

            if success_count > 0:
                st.success(f"✅ Synced {success_count} templates to files successfully!")
            if error_count > 0:
                st.warning(f"⚠️ {error_count} verticals had sync errors.")

with col2:
    if st.button("📤 Import Templates from Files", use_container_width=True):
        from integrations import sync_templates_to_db

        verticals = models.get_verticals(active_only=True)

        if not verticals:
            st.warning("No verticals found to import.")
        else:
            success_count = 0
            error_count = 0

            with st.spinner("Importing templates..."):
                for vertical in verticals:
                    try:
                        imported = sync_templates_to_db(vertical['vertical_id'])
                        success_count += len(imported)
                    except Exception as e:
                        st.warning(f"Error importing {vertical['vertical_id']}: {e}")
                        error_count += 1

            if success_count > 0:
                st.success(f"✅ Imported {success_count} templates from files successfully!")
            if error_count > 0:
                st.warning(f"⚠️ {error_count} verticals had import errors.")

            if success_count > 0:
                st.cache_data.clear()
                st.rerun()

# Refresh button
st.markdown("---")
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
