"""
Database Models Module
Campaign Control Center Dashboard

Provides CRUD operations for all database entities.
All functions use parameterized queries to prevent SQL injection.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from . import schema
from . import encryption


# ============================================================================
# VERTICALS - CRUD Operations
# ============================================================================

def get_verticals(active_only: bool = False) -> List[Dict[str, Any]]:
    """
    Get all verticals from the database.

    Args:
        active_only: If True, only return active verticals

    Returns:
        List of vertical dictionaries
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute('''
                SELECT * FROM verticals WHERE active = 1
                ORDER BY display_name
            ''')
        else:
            cursor.execute('''
                SELECT * FROM verticals ORDER BY display_name
            ''')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(f"Failed to get verticals: {str(e)}")


def get_vertical(vertical_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single vertical by ID.

    Args:
        vertical_id: The vertical ID to retrieve

    Returns:
        Vertical dictionary or None if not found
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM verticals WHERE vertical_id = ?
        ''', (vertical_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    except Exception as e:
        raise RuntimeError(f"Failed to get vertical: {str(e)}")


def create_vertical(
    vertical_id: str,
    display_name: str,
    csv_filename: str,
    target_industry: Optional[str] = None,
    active: bool = True
) -> bool:
    """
    Create a new vertical.

    Args:
        vertical_id: Unique identifier (e.g., 'debarment')
        display_name: Human-readable name (e.g., 'Debarment Monitor')
        csv_filename: CSV filename for prospects (e.g., 'debarment_prospects.csv')
        target_industry: Target industry description
        active: Whether the vertical is active

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If required fields are empty
        RuntimeError: If database operation fails
    """
    if not vertical_id or not display_name or not csv_filename:
        raise ValueError("vertical_id, display_name, and csv_filename are required")

    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO verticals (
                vertical_id, display_name, target_industry,
                csv_filename, active
            ) VALUES (?, ?, ?, ?, ?)
        ''', (vertical_id, display_name, target_industry, csv_filename, active))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        raise ValueError(f"Vertical with ID '{vertical_id}' already exists")
    except Exception as e:
        raise RuntimeError(f"Failed to create vertical: {str(e)}")


def update_vertical(vertical_id: str, **kwargs) -> bool:
    """
    Update a vertical's fields.

    Args:
        vertical_id: The vertical ID to update
        **kwargs: Fields to update (display_name, target_industry, csv_filename, active)

    Returns:
        True if successful, False if vertical not found

    Raises:
        RuntimeError: If database operation fails
    """
    allowed_fields = ['display_name', 'target_industry', 'csv_filename', 'active']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        # Build SET clause
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        set_clause += ', updated_at = CURRENT_TIMESTAMP'

        query = f"UPDATE verticals SET {set_clause} WHERE vertical_id = ?"
        values = list(updates.values()) + [vertical_id]

        cursor.execute(query, values)
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to update vertical: {str(e)}")


def delete_vertical(vertical_id: str) -> bool:
    """
    Delete a vertical (cascade deletes templates and assignments).

    Args:
        vertical_id: The vertical ID to delete

    Returns:
        True if successful, False if vertical not found

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM verticals WHERE vertical_id = ?', (vertical_id,))
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to delete vertical: {str(e)}")


def toggle_vertical_active(vertical_id: str, active: bool) -> bool:
    """
    Toggle a vertical's active status.

    Args:
        vertical_id: The vertical ID
        active: New active status

    Returns:
        True if successful, False if vertical not found
    """
    return update_vertical(vertical_id, active=active)


# ============================================================================
# EMAIL ACCOUNTS - CRUD Operations
# ============================================================================

def get_email_accounts(active_only: bool = False) -> List[Dict[str, Any]]:
    """
    Get all email accounts from the database.

    Args:
        active_only: If True, only return active accounts

    Returns:
        List of account dictionaries (passwords remain encrypted)
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute('''
                SELECT * FROM email_accounts WHERE active = 1
                ORDER BY email_address
            ''')
        else:
            cursor.execute('''
                SELECT * FROM email_accounts ORDER BY email_address
            ''')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(f"Failed to get email accounts: {str(e)}")


def get_email_account(account_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single email account by ID.

    Args:
        account_id: The account ID to retrieve

    Returns:
        Account dictionary or None if not found
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM email_accounts WHERE account_id = ?
        ''', (account_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    except Exception as e:
        raise RuntimeError(f"Failed to get email account: {str(e)}")


def create_email_account(
    email_address: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    password: str,
    daily_send_limit: int,
    display_name: Optional[str] = None,
    active: bool = True
) -> int:
    """
    Create a new email account with encrypted password.

    Args:
        email_address: Email address
        smtp_host: SMTP server host
        smtp_port: SMTP server port
        smtp_username: SMTP username
        password: Plain-text password (will be encrypted)
        daily_send_limit: Daily send limit
        display_name: Display name for the account
        active: Whether the account is active

    Returns:
        The new account_id

    Raises:
        ValueError: If required fields are empty or invalid
        RuntimeError: If database operation fails
    """
    if not all([email_address, smtp_host, smtp_username, password]):
        raise ValueError("email_address, smtp_host, smtp_username, and password are required")

    if smtp_port <= 0 or smtp_port > 65535:
        raise ValueError("smtp_port must be between 1 and 65535")

    if daily_send_limit <= 0:
        raise ValueError("daily_send_limit must be greater than 0")

    try:
        # Encrypt password
        password_encrypted = encryption.encrypt_password(password)

        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO email_accounts (
                email_address, display_name, smtp_host, smtp_port,
                smtp_username, password_encrypted, daily_send_limit, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_address, display_name, smtp_host, smtp_port,
            smtp_username, password_encrypted, daily_send_limit, active
        ))

        account_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return account_id

    except sqlite3.IntegrityError:
        raise ValueError(f"Email account '{email_address}' already exists")
    except Exception as e:
        raise RuntimeError(f"Failed to create email account: {str(e)}")


def update_email_account(account_id: int, **kwargs) -> bool:
    """
    Update an email account's fields.

    Args:
        account_id: The account ID to update
        **kwargs: Fields to update (email_address, display_name, smtp_host,
                  smtp_port, smtp_username, password, daily_send_limit, active)
                  Note: 'password' will be encrypted automatically

    Returns:
        True if successful, False if account not found

    Raises:
        RuntimeError: If database operation fails
    """
    allowed_fields = [
        'email_address', 'display_name', 'smtp_host', 'smtp_port',
        'smtp_username', 'daily_send_limit', 'active'
    ]

    # Handle password separately (needs encryption)
    if 'password' in kwargs:
        try:
            kwargs['password_encrypted'] = encryption.encrypt_password(kwargs['password'])
            del kwargs['password']
            allowed_fields.append('password_encrypted')
        except Exception as e:
            raise RuntimeError(f"Failed to encrypt password: {str(e)}")

    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        # Build SET clause
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        set_clause += ', updated_at = CURRENT_TIMESTAMP'

        query = f"UPDATE email_accounts SET {set_clause} WHERE account_id = ?"
        values = list(updates.values()) + [account_id]

        cursor.execute(query, values)
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to update email account: {str(e)}")


def delete_email_account(account_id: int) -> bool:
    """
    Delete an email account (cascade deletes assignments).

    Args:
        account_id: The account ID to delete

    Returns:
        True if successful, False if account not found

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM email_accounts WHERE account_id = ?', (account_id,))
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to delete email account: {str(e)}")


def toggle_account_active(account_id: int, active: bool) -> bool:
    """
    Toggle an account's active status.

    Args:
        account_id: The account ID
        active: New active status

    Returns:
        True if successful, False if account not found
    """
    return update_email_account(account_id, active=active)


def get_account_password_decrypted(account_id: int) -> Optional[str]:
    """
    Get the decrypted password for an account.

    Args:
        account_id: The account ID

    Returns:
        Decrypted password or None if account not found

    Raises:
        RuntimeError: If decryption fails
    """
    try:
        account = get_email_account(account_id)
        if not account:
            return None

        password_encrypted = account['password_encrypted']
        return encryption.decrypt_password(password_encrypted)

    except Exception as e:
        raise RuntimeError(f"Failed to decrypt password: {str(e)}")


# ============================================================================
# ACCOUNT-VERTICAL ASSIGNMENTS - CRUD Operations
# ============================================================================

def assign_account_to_vertical(account_id: int, vertical_id: str) -> bool:
    """
    Assign an email account to a vertical.

    Args:
        account_id: The account ID
        vertical_id: The vertical ID

    Returns:
        True if successful

    Raises:
        ValueError: If assignment already exists
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO account_verticals (account_id, vertical_id)
            VALUES (?, ?)
        ''', (account_id, vertical_id))

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:
        raise ValueError(f"Account {account_id} is already assigned to vertical '{vertical_id}'")
    except Exception as e:
        raise RuntimeError(f"Failed to assign account to vertical: {str(e)}")


def unassign_account_from_vertical(account_id: int, vertical_id: str) -> bool:
    """
    Unassign an email account from a vertical.

    Args:
        account_id: The account ID
        vertical_id: The vertical ID

    Returns:
        True if successful, False if assignment not found

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM account_verticals
            WHERE account_id = ? AND vertical_id = ?
        ''', (account_id, vertical_id))

        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to unassign account from vertical: {str(e)}")


def get_account_verticals(account_id: int) -> List[str]:
    """
    Get all verticals assigned to an account.

    Args:
        account_id: The account ID

    Returns:
        List of vertical IDs
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT vertical_id FROM account_verticals
            WHERE account_id = ?
            ORDER BY vertical_id
        ''', (account_id,))

        rows = cursor.fetchall()
        conn.close()

        return [row['vertical_id'] for row in rows]

    except Exception as e:
        raise RuntimeError(f"Failed to get account verticals: {str(e)}")


def get_vertical_accounts(vertical_id: str) -> List[Dict[str, Any]]:
    """
    Get all accounts assigned to a vertical.

    Args:
        vertical_id: The vertical ID

    Returns:
        List of account dictionaries
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT ea.*
            FROM email_accounts ea
            INNER JOIN account_verticals av ON ea.account_id = av.account_id
            WHERE av.vertical_id = ?
            ORDER BY ea.email_address
        ''', (vertical_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(f"Failed to get vertical accounts: {str(e)}")


def get_assignment_matrix() -> Dict[int, List[str]]:
    """
    Get the full account-vertical assignment matrix.

    Returns:
        Dictionary mapping account_id to list of vertical_ids
        Example: {1: ['debarment', 'food_recall'], 2: ['grant_alerts']}
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT account_id, vertical_id FROM account_verticals
            ORDER BY account_id, vertical_id
        ''')

        rows = cursor.fetchall()
        conn.close()

        matrix = {}
        for row in rows:
            account_id = row['account_id']
            vertical_id = row['vertical_id']

            if account_id not in matrix:
                matrix[account_id] = []

            matrix[account_id].append(vertical_id)

        return matrix

    except Exception as e:
        raise RuntimeError(f"Failed to get assignment matrix: {str(e)}")


# ============================================================================
# EMAIL TEMPLATES - CRUD Operations
# ============================================================================

def get_templates(
    vertical_id: Optional[str] = None,
    template_type: Optional[str] = None,
    active_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Get templates with optional filters.

    Args:
        vertical_id: Filter by vertical ID
        template_type: Filter by type ('initial' or 'followup')
        active_only: If True, only return active templates

    Returns:
        List of template dictionaries
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM email_templates WHERE 1=1'
        params = []

        if vertical_id:
            query += ' AND vertical_id = ?'
            params.append(vertical_id)

        if template_type:
            query += ' AND template_type = ?'
            params.append(template_type)

        if active_only:
            query += ' AND active = 1'

        query += ' ORDER BY vertical_id, template_type, template_name'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(f"Failed to get templates: {str(e)}")


def get_template(template_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single template by ID.

    Args:
        template_id: The template ID to retrieve

    Returns:
        Template dictionary or None if not found
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM email_templates WHERE template_id = ?
        ''', (template_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    except Exception as e:
        raise RuntimeError(f"Failed to get template: {str(e)}")


def create_template(
    vertical_id: str,
    template_type: str,
    template_name: str,
    subject_line: str,
    email_body: str,
    active: bool = True
) -> int:
    """
    Create a new email template.

    Args:
        vertical_id: The vertical ID
        template_type: Template type ('initial' or 'followup')
        template_name: Template name
        subject_line: Email subject line
        email_body: Email body text
        active: Whether the template is active

    Returns:
        The new template_id

    Raises:
        ValueError: If required fields are empty or invalid
        RuntimeError: If database operation fails
    """
    if not all([vertical_id, template_type, template_name, subject_line, email_body]):
        raise ValueError("All template fields are required")

    if template_type not in ['initial', 'followup']:
        raise ValueError("template_type must be 'initial' or 'followup'")

    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO email_templates (
                vertical_id, template_type, template_name,
                subject_line, email_body, active
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (vertical_id, template_type, template_name, subject_line, email_body, active))

        template_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return template_id

    except sqlite3.IntegrityError:
        raise ValueError(
            f"Template '{template_name}' of type '{template_type}' "
            f"already exists for vertical '{vertical_id}'"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create template: {str(e)}")


def update_template(template_id: int, **kwargs) -> bool:
    """
    Update a template's fields.

    Args:
        template_id: The template ID to update
        **kwargs: Fields to update (template_name, subject_line, email_body, active)

    Returns:
        True if successful, False if template not found

    Raises:
        RuntimeError: If database operation fails
    """
    allowed_fields = ['template_name', 'subject_line', 'email_body', 'active']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        # Build SET clause
        set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
        set_clause += ', updated_at = CURRENT_TIMESTAMP'

        query = f"UPDATE email_templates SET {set_clause} WHERE template_id = ?"
        values = list(updates.values()) + [template_id]

        cursor.execute(query, values)
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to update template: {str(e)}")


def delete_template(template_id: int) -> bool:
    """
    Delete a template.

    Args:
        template_id: The template ID to delete

    Returns:
        True if successful, False if template not found

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM email_templates WHERE template_id = ?', (template_id,))
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to delete template: {str(e)}")


def toggle_template_active(template_id: int, active: bool) -> bool:
    """
    Toggle a template's active status.

    Args:
        template_id: The template ID
        active: New active status

    Returns:
        True if successful, False if template not found
    """
    return update_template(template_id, active=active)


def get_active_template(vertical_id: str, template_type: str) -> Optional[Dict[str, Any]]:
    """
    Get the active template for a vertical and type.

    Args:
        vertical_id: The vertical ID
        template_type: Template type ('initial' or 'followup')

    Returns:
        Template dictionary or None if not found
    """
    templates = get_templates(vertical_id, template_type, active_only=True)
    return templates[0] if templates else None


# ============================================================================
# CAMPAIGN SETTINGS - CRUD Operations
# ============================================================================

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a setting value by key.

    Args:
        key: Setting key
        default: Default value if setting not found

    Returns:
        Setting value or default
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT setting_value FROM campaign_settings WHERE setting_key = ?
        ''', (key,))

        row = cursor.fetchone()
        conn.close()

        return row['setting_value'] if row else default

    except Exception as e:
        raise RuntimeError(f"Failed to get setting: {str(e)}")


def set_setting(key: str, value: str, description: Optional[str] = None) -> bool:
    """
    Set a setting value (insert or update).

    Args:
        key: Setting key
        value: Setting value
        description: Optional description

    Returns:
        True if successful

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO campaign_settings (setting_key, setting_value, description)
            VALUES (?, ?, ?)
            ON CONFLICT(setting_key) DO UPDATE SET
                setting_value = excluded.setting_value,
                description = COALESCE(excluded.description, description),
                updated_at = CURRENT_TIMESTAMP
        ''', (key, value, description))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        raise RuntimeError(f"Failed to set setting: {str(e)}")


def get_all_settings() -> Dict[str, str]:
    """
    Get all settings as a dictionary.

    Returns:
        Dictionary mapping setting keys to values
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT setting_key, setting_value FROM campaign_settings')
        rows = cursor.fetchall()
        conn.close()

        return {row['setting_key']: row['setting_value'] for row in rows}

    except Exception as e:
        raise RuntimeError(f"Failed to get all settings: {str(e)}")


def delete_setting(key: str) -> bool:
    """
    Delete a setting.

    Args:
        key: Setting key to delete

    Returns:
        True if successful, False if setting not found

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        conn = schema.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM campaign_settings WHERE setting_key = ?', (key,))
        rows_affected = cursor.rowcount

        conn.commit()
        conn.close()

        return rows_affected > 0

    except Exception as e:
        raise RuntimeError(f"Failed to delete setting: {str(e)}")
