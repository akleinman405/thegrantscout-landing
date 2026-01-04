"""
Database Schema Module
Campaign Control Center Dashboard

Defines the SQLite database schema and provides initialization functions.
"""

import sqlite3
import os
from typing import Optional


def get_database_path() -> str:
    """
    Get the path to the SQLite database file.

    Returns:
        str: Full path to the database file
    """
    # Database stored in the outreach_sequences directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_dir = os.path.dirname(module_dir)
    sequences_dir = os.path.dirname(dashboard_dir)
    return os.path.join(sequences_dir, 'campaign_control.db')


def database_exists() -> bool:
    """
    Check if the database file exists.

    Returns:
        bool: True if database exists, False otherwise
    """
    return os.path.exists(get_database_path())


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the database.

    Returns:
        sqlite3.Connection: Database connection

    Raises:
        RuntimeError: If database connection fails
    """
    try:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        # Enable foreign key constraints (required for cascade deletes)
        conn.execute("PRAGMA foreign_keys = ON")

        return conn
    except Exception as e:
        raise RuntimeError(f"Failed to connect to database: {str(e)}")


def create_schema() -> None:
    """
    Create all database tables and indexes.

    This function is idempotent - it can be safely called multiple times.
    Tables are created with IF NOT EXISTS clause.

    Raises:
        RuntimeError: If schema creation fails
    """
    try:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")

        # ============================================================================
        # TABLE: verticals
        # Stores vertical/business line metadata
        # ============================================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verticals (
                vertical_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                target_industry TEXT,
                csv_filename TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ============================================================================
        # TABLE: email_accounts
        # Stores SMTP account credentials and settings
        # ============================================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_address TEXT UNIQUE NOT NULL,
                display_name TEXT,
                smtp_host TEXT NOT NULL,
                smtp_port INTEGER NOT NULL,
                smtp_username TEXT NOT NULL,
                password_encrypted BLOB NOT NULL,
                daily_send_limit INTEGER NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ============================================================================
        # TABLE: account_verticals
        # Many-to-many relationship: which accounts handle which verticals
        # ============================================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_verticals (
                account_id INTEGER NOT NULL,
                vertical_id TEXT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (account_id, vertical_id),
                FOREIGN KEY (account_id) REFERENCES email_accounts(account_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (vertical_id) REFERENCES verticals(vertical_id)
                    ON DELETE CASCADE
            )
        ''')

        # ============================================================================
        # TABLE: email_templates
        # Stores email templates (subject + body)
        # ============================================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vertical_id TEXT NOT NULL,
                template_type TEXT NOT NULL,
                template_name TEXT NOT NULL,
                subject_line TEXT NOT NULL,
                email_body TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vertical_id) REFERENCES verticals(vertical_id)
                    ON DELETE CASCADE,
                UNIQUE(vertical_id, template_type, template_name)
            )
        ''')

        # ============================================================================
        # TABLE: campaign_settings
        # Global settings (business hours, pacing, etc.)
        # ============================================================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ============================================================================
        # INDEXES for performance
        # ============================================================================
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_templates_vertical
            ON email_templates(vertical_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_templates_type
            ON email_templates(template_type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_account_verticals_account
            ON account_verticals(account_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_account_verticals_vertical
            ON account_verticals(vertical_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_email_accounts_active
            ON email_accounts(active)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_verticals_active
            ON verticals(active)
        ''')

        conn.commit()
        conn.close()

    except Exception as e:
        raise RuntimeError(f"Failed to create database schema: {str(e)}")


def seed_default_settings() -> None:
    """
    Insert default settings into the campaign_settings table.

    This function is idempotent - it only inserts settings that don't exist.

    Raises:
        RuntimeError: If seeding fails
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        default_settings = [
            ('business_hours_start', '9', 'Business hours start (hour, 24-hour format)'),
            ('business_hours_end', '15', 'Business hours end (hour, 24-hour format)'),
            ('timezone', 'US/Eastern', 'Timezone for business hours'),
            ('conservative_pacing', 'true', 'Enable conservative pacing between emails'),
            ('base_delay_min', '5', 'Minimum delay between emails (minutes)'),
            ('base_delay_max', '10', 'Maximum delay between emails (minutes)'),
        ]

        for key, value, description in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO campaign_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (key, value, description))

        conn.commit()
        conn.close()

    except Exception as e:
        raise RuntimeError(f"Failed to seed default settings: {str(e)}")


def init_database() -> None:
    """
    Initialize the database: create schema and seed default settings.

    This is the main function to call for first-time database setup.

    Raises:
        RuntimeError: If initialization fails
    """
    try:
        create_schema()
        seed_default_settings()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize database: {str(e)}")


def verify_schema() -> bool:
    """
    Verify that all tables exist in the database.

    Returns:
        bool: True if all tables exist, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        required_tables = [
            'verticals',
            'email_accounts',
            'account_verticals',
            'email_templates',
            'campaign_settings'
        ]

        for table_name in required_tables:
            cursor.execute('''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            ''', (table_name,))

            if cursor.fetchone() is None:
                conn.close()
                return False

        conn.close()
        return True

    except Exception:
        return False


if __name__ == "__main__":
    # Test schema creation when run directly
    print("Testing database schema...")
    print(f"Database path: {get_database_path()}")

    try:
        init_database()
        print("✓ Schema created successfully!")

        if verify_schema():
            print("✓ All tables verified!")
        else:
            print("✗ Schema verification failed!")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
