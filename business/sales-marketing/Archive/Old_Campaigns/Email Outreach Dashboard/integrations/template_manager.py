"""
Email template file management.
Handles reading, writing, and syncing templates between files and database.
"""

import os
from typing import List, Dict, Tuple, Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.windows_paths import get_template_directory, get_template_file_path
from utils.validators import sanitize_filename


def save_template_to_file(
    vertical_id: str,
    template_type: str,
    name: str,
    content: str
) -> bool:
    """
    Save an email template to a file.

    Args:
        vertical_id: The vertical identifier
        template_type: 'initial' or 'followup'
        name: Template name
        content: Template content (subject + body)

    Returns:
        bool: True if successful
    """
    if template_type not in ['initial', 'followup']:
        raise ValueError(f"Invalid template type: {template_type}")

    # Sanitize name for filesystem
    safe_name = sanitize_filename(name)

    file_path = get_template_file_path(vertical_id, template_type, safe_name)

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write template content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        raise IOError(f"Error saving template to file: {str(e)}")


def read_template_from_file(
    vertical_id: str,
    template_type: str,
    name: str
) -> str:
    """
    Read an email template from a file.

    Args:
        vertical_id: The vertical identifier
        template_type: 'initial' or 'followup'
        name: Template name

    Returns:
        str: Template content

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if template_type not in ['initial', 'followup']:
        raise ValueError(f"Invalid template type: {template_type}")

    safe_name = sanitize_filename(name)
    file_path = get_template_file_path(vertical_id, template_type, safe_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Template file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    except Exception as e:
        raise IOError(f"Error reading template from file: {str(e)}")


def list_template_files(vertical_id: str) -> List[Dict]:
    """
    List all template files for a vertical.

    Args:
        vertical_id: The vertical identifier

    Returns:
        List[Dict]: List of template file information
    """
    templates_dir = get_template_directory(vertical_id)

    if not os.path.exists(templates_dir):
        return []

    templates = []

    try:
        for filename in os.listdir(templates_dir):
            if filename.endswith('.txt'):
                # Parse filename: {type}_{name}.txt
                parts = filename.rsplit('.txt', 1)[0].split('_', 1)

                if len(parts) == 2:
                    template_type, template_name = parts

                    if template_type in ['initial', 'followup']:
                        file_path = os.path.join(templates_dir, filename)
                        file_size = os.path.getsize(file_path)
                        modified_time = os.path.getmtime(file_path)

                        templates.append({
                            'vertical_id': vertical_id,
                            'template_type': template_type,
                            'name': template_name,
                            'filename': filename,
                            'file_path': file_path,
                            'size_bytes': file_size,
                            'modified_timestamp': modified_time
                        })

    except Exception as e:
        raise IOError(f"Error listing template files: {str(e)}")

    return templates


def delete_template_file(vertical_id: str, template_type: str, name: str) -> bool:
    """
    Delete a template file.

    Args:
        vertical_id: The vertical identifier
        template_type: 'initial' or 'followup'
        name: Template name

    Returns:
        bool: True if deleted, False if file didn't exist
    """
    safe_name = sanitize_filename(name)
    file_path = get_template_file_path(vertical_id, template_type, safe_name)

    if not os.path.exists(file_path):
        return False

    try:
        os.remove(file_path)
        return True
    except Exception as e:
        raise IOError(f"Error deleting template file: {str(e)}")


def sync_templates_to_db(vertical_id: str) -> List[Dict]:
    """
    Sync template files to database.
    Reads all template files and returns data to be inserted into database.

    Args:
        vertical_id: The vertical identifier

    Returns:
        List[Dict]: List of template data dictionaries for database insertion
    """
    # Import here to avoid circular dependency
    try:
        from database import models
    except ImportError:
        raise ImportError("Database models not available for syncing")

    template_files = list_template_files(vertical_id)
    synced_templates = []

    for template_file in template_files:
        try:
            # Read content from file
            content = read_template_from_file(
                vertical_id,
                template_file['template_type'],
                template_file['name']
            )

            # Parse content (assuming format: subject line on first line, body follows)
            lines = content.split('\n', 1)
            subject_line = lines[0].strip() if len(lines) > 0 else ''
            email_body = lines[1].strip() if len(lines) > 1 else content

            # Check if template exists in database
            existing_templates = models.get_templates(
                vertical_id=vertical_id,
                template_type=template_file['template_type']
            )

            template_exists = any(
                t['template_name'] == template_file['name']
                for t in existing_templates
            )

            if not template_exists:
                # Create in database
                template_id = models.create_template(
                    vertical_id=vertical_id,
                    template_type=template_file['template_type'],
                    template_name=template_file['name'],
                    subject_line=subject_line,
                    email_body=email_body
                )

                synced_templates.append({
                    'template_id': template_id,
                    'name': template_file['name'],
                    'type': template_file['template_type'],
                    'action': 'created'
                })

        except Exception as e:
            # Log error but continue with other templates
            print(f"Error syncing template {template_file['name']}: {str(e)}")
            continue

    return synced_templates


def sync_templates_from_db(vertical_id: str) -> List[Dict]:
    """
    Sync database templates to files.
    Reads all templates from database and writes them to files.

    Args:
        vertical_id: The vertical identifier

    Returns:
        List[Dict]: List of synced template information
    """
    # Import here to avoid circular dependency
    try:
        from database import models
    except ImportError:
        raise ImportError("Database models not available for syncing")

    templates = models.get_templates(vertical_id=vertical_id, active_only=True)
    synced_templates = []

    for template in templates:
        try:
            # Combine subject and body for file storage
            content = f"{template['subject_line']}\n{template['email_body']}"

            # Save to file
            save_template_to_file(
                vertical_id=vertical_id,
                template_type=template['template_type'],
                name=template['template_name'],
                content=content
            )

            synced_templates.append({
                'name': template['template_name'],
                'type': template['template_type'],
                'action': 'synced_to_file'
            })

        except Exception as e:
            # Log error but continue with other templates
            print(f"Error syncing template {template['template_name']} to file: {str(e)}")
            continue

    return synced_templates


def export_template_bundle(vertical_id: str, output_dir: str) -> bool:
    """
    Export all templates for a vertical to a specified directory.

    Args:
        vertical_id: The vertical identifier
        output_dir: Directory to export templates to

    Returns:
        bool: True if successful
    """
    import shutil

    templates_dir = get_template_directory(vertical_id)

    if not os.path.exists(templates_dir):
        raise FileNotFoundError(f"No templates found for vertical: {vertical_id}")

    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Copy all template files
        for filename in os.listdir(templates_dir):
            if filename.endswith('.txt'):
                src_path = os.path.join(templates_dir, filename)
                dst_path = os.path.join(output_dir, filename)
                shutil.copy2(src_path, dst_path)

        return True

    except Exception as e:
        raise IOError(f"Error exporting template bundle: {str(e)}")


def import_template_bundle(vertical_id: str, input_dir: str) -> int:
    """
    Import templates from a directory.

    Args:
        vertical_id: The vertical identifier
        input_dir: Directory containing template files

    Returns:
        int: Number of templates imported
    """
    import shutil

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Import directory not found: {input_dir}")

    templates_dir = get_template_directory(vertical_id)
    count = 0

    try:
        for filename in os.listdir(input_dir):
            if filename.endswith('.txt'):
                src_path = os.path.join(input_dir, filename)
                dst_path = os.path.join(templates_dir, filename)
                shutil.copy2(src_path, dst_path)
                count += 1

        return count

    except Exception as e:
        raise IOError(f"Error importing template bundle: {str(e)}")
