"""
Database Package
Campaign Control Center Dashboard

This package provides all database functionality for the dashboard.

Main modules:
- schema: Database schema definition and initialization
- models: CRUD operations for all entities
- encryption: Password encryption utilities
- migrations: Data migration and backup utilities

Usage:
    from database import models, schema

    # Initialize database
    if not schema.database_exists():
        schema.init_database()

    # Create a vertical
    models.create_vertical(
        vertical_id='debarment',
        display_name='Debarment Monitor',
        csv_filename='debarment_prospects.csv'
    )

    # Get all verticals
    verticals = models.get_verticals()
"""

# Import main functions for easy access
from .schema import (
    get_database_path,
    database_exists,
    get_connection,
    create_schema,
    init_database,
    verify_schema,
)

from .models import (
    # Verticals
    get_verticals,
    get_vertical,
    create_vertical,
    update_vertical,
    delete_vertical,
    toggle_vertical_active,

    # Email Accounts
    get_email_accounts,
    get_email_account,
    create_email_account,
    update_email_account,
    delete_email_account,
    toggle_account_active,
    get_account_password_decrypted,

    # Account-Vertical Assignments
    assign_account_to_vertical,
    unassign_account_from_vertical,
    get_account_verticals,
    get_vertical_accounts,
    get_assignment_matrix,

    # Email Templates
    get_templates,
    get_template,
    create_template,
    update_template,
    delete_template,
    toggle_template_active,
    get_active_template,

    # Campaign Settings
    get_setting,
    set_setting,
    get_all_settings,
    delete_setting,
)

from .encryption import (
    encrypt_password,
    decrypt_password,
    test_encryption,
)

from .migrations import (
    backup_database,
    export_database_to_json,
    import_database_from_json,
    seed_sample_data,
    get_database_stats,
    verify_database_integrity,
)


__all__ = [
    # Schema
    'get_database_path',
    'database_exists',
    'get_connection',
    'create_schema',
    'init_database',
    'verify_schema',

    # Verticals
    'get_verticals',
    'get_vertical',
    'create_vertical',
    'update_vertical',
    'delete_vertical',
    'toggle_vertical_active',

    # Email Accounts
    'get_email_accounts',
    'get_email_account',
    'create_email_account',
    'update_email_account',
    'delete_email_account',
    'toggle_account_active',
    'get_account_password_decrypted',

    # Account-Vertical Assignments
    'assign_account_to_vertical',
    'unassign_account_from_vertical',
    'get_account_verticals',
    'get_vertical_accounts',
    'get_assignment_matrix',

    # Email Templates
    'get_templates',
    'get_template',
    'create_template',
    'update_template',
    'delete_template',
    'toggle_template_active',
    'get_active_template',

    # Campaign Settings
    'get_setting',
    'set_setting',
    'get_all_settings',
    'delete_setting',

    # Encryption
    'encrypt_password',
    'decrypt_password',
    'test_encryption',

    # Migrations
    'backup_database',
    'export_database_to_json',
    'import_database_from_json',
    'seed_sample_data',
    'get_database_stats',
    'verify_database_integrity',
]


__version__ = '1.0.0'
