"""
Database Migrations Module
Campaign Control Center Dashboard

Provides utilities for migrating existing data, backup, and export/import operations.
"""

import os
import json
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime

from . import schema
from . import models


def backup_database(backup_dir: Optional[str] = None) -> str:
    """
    Create a backup of the database file.

    Args:
        backup_dir: Directory to store backup (defaults to same directory as database)

    Returns:
        Path to the backup file

    Raises:
        RuntimeError: If backup fails
    """
    try:
        db_path = schema.get_database_path()

        if not os.path.exists(db_path):
            raise RuntimeError("Database file does not exist")

        # Default backup directory is same as database
        if backup_dir is None:
            backup_dir = os.path.dirname(db_path)

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"campaign_control_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Copy database file
        shutil.copy2(db_path, backup_path)

        return backup_path

    except Exception as e:
        raise RuntimeError(f"Failed to backup database: {str(e)}")


def export_database_to_json(export_path: str) -> None:
    """
    Export all database tables to a JSON file.

    Args:
        export_path: Path to the JSON export file

    Raises:
        RuntimeError: If export fails
    """
    try:
        export_data = {
            'export_date': datetime.now().isoformat(),
            'verticals': models.get_verticals(),
            'email_accounts': models.get_email_accounts(),
            'account_verticals': models.get_assignment_matrix(),
            'email_templates': models.get_templates(),
            'campaign_settings': models.get_all_settings()
        }

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

    except Exception as e:
        raise RuntimeError(f"Failed to export database: {str(e)}")


def import_database_from_json(import_path: str, clear_existing: bool = False) -> Dict[str, int]:
    """
    Import database tables from a JSON file.

    Args:
        import_path: Path to the JSON import file
        clear_existing: If True, clear existing data before import

    Returns:
        Dictionary with import statistics

    Raises:
        RuntimeError: If import fails
    """
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        stats = {
            'verticals_imported': 0,
            'accounts_imported': 0,
            'assignments_imported': 0,
            'templates_imported': 0,
            'settings_imported': 0,
            'errors': []
        }

        # Clear existing data if requested
        if clear_existing:
            # Note: This is destructive! Use with caution
            conn = schema.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM email_templates')
            cursor.execute('DELETE FROM account_verticals')
            cursor.execute('DELETE FROM email_accounts')
            cursor.execute('DELETE FROM verticals')
            cursor.execute('DELETE FROM campaign_settings')
            conn.commit()
            conn.close()

        # Import verticals
        for vertical in import_data.get('verticals', []):
            try:
                models.create_vertical(
                    vertical_id=vertical['vertical_id'],
                    display_name=vertical['display_name'],
                    csv_filename=vertical['csv_filename'],
                    target_industry=vertical.get('target_industry'),
                    active=vertical.get('active', True)
                )
                stats['verticals_imported'] += 1
            except Exception as e:
                stats['errors'].append(f"Vertical {vertical['vertical_id']}: {str(e)}")

        # Import email accounts
        for account in import_data.get('email_accounts', []):
            try:
                # Note: Passwords cannot be imported directly as they're encrypted
                # with a specific key. Skip account import or handle separately.
                stats['errors'].append(
                    f"Account {account['email_address']}: "
                    "Cannot import encrypted passwords automatically"
                )
            except Exception as e:
                stats['errors'].append(f"Account {account['email_address']}: {str(e)}")

        # Import templates
        for template in import_data.get('email_templates', []):
            try:
                models.create_template(
                    vertical_id=template['vertical_id'],
                    template_type=template['template_type'],
                    template_name=template['template_name'],
                    subject_line=template['subject_line'],
                    email_body=template['email_body'],
                    active=template.get('active', True)
                )
                stats['templates_imported'] += 1
            except Exception as e:
                stats['errors'].append(
                    f"Template {template['template_name']}: {str(e)}"
                )

        # Import settings
        for key, value in import_data.get('campaign_settings', {}).items():
            try:
                models.set_setting(key, value)
                stats['settings_imported'] += 1
            except Exception as e:
                stats['errors'].append(f"Setting {key}: {str(e)}")

        return stats

    except Exception as e:
        raise RuntimeError(f"Failed to import database: {str(e)}")


def migrate_from_existing_config(config_path: str) -> Dict[str, int]:
    """
    Migrate data from existing config.py file.

    This function reads the existing config.py and populates the database
    with verticals and templates.

    Args:
        config_path: Path to config.py file

    Returns:
        Dictionary with migration statistics

    Raises:
        RuntimeError: If migration fails
    """
    try:
        stats = {
            'verticals_migrated': 0,
            'templates_migrated': 0,
            'errors': []
        }

        # Read config.py
        # Note: This is a simplified implementation
        # In practice, you'd need to parse the Python file or import it
        stats['errors'].append(
            "migrate_from_existing_config: Manual implementation required. "
            "This function needs to be customized based on your config.py structure."
        )

        return stats

    except Exception as e:
        raise RuntimeError(f"Failed to migrate from config: {str(e)}")


def seed_sample_data() -> Dict[str, int]:
    """
    Seed the database with sample data for testing.

    Returns:
        Dictionary with seeding statistics

    Raises:
        RuntimeError: If seeding fails
    """
    try:
        stats = {
            'verticals_created': 0,
            'accounts_created': 0,
            'assignments_created': 0,
            'templates_created': 0,
            'errors': []
        }

        # Create sample verticals
        sample_verticals = [
            {
                'vertical_id': 'debarment',
                'display_name': 'Debarment Monitor',
                'target_industry': 'Federal Contractors',
                'csv_filename': 'debarment_prospects.csv'
            },
            {
                'vertical_id': 'food_recall',
                'display_name': 'Food Recall Alerts',
                'target_industry': 'Food & Beverage',
                'csv_filename': 'food_recall_prospects.csv'
            },
            {
                'vertical_id': 'grant_alerts',
                'display_name': 'Grant Opportunities',
                'target_industry': 'Nonprofits & Government',
                'csv_filename': 'grant_alerts_prospects.csv'
            }
        ]

        for vertical in sample_verticals:
            try:
                models.create_vertical(**vertical)
                stats['verticals_created'] += 1
            except ValueError:
                # Already exists, skip
                pass
            except Exception as e:
                stats['errors'].append(f"Vertical {vertical['vertical_id']}: {str(e)}")

        # Create sample templates
        sample_templates = [
            {
                'vertical_id': 'debarment',
                'template_type': 'initial',
                'template_name': 'Default Initial',
                'subject_line': 'Debarment monitoring question',
                'email_body': '''Hi{greeting},

I wanted to reach out because I noticed {company} works with federal agencies.

Are you currently monitoring the SAM.gov debarment list to ensure your subcontractors and partners aren't excluded from federal contracting?

We've built a tool that automatically monitors this for you and sends alerts if anyone in your network gets flagged.

Would you be interested in learning more?

Best regards'''
            },
            {
                'vertical_id': 'debarment',
                'template_type': 'followup',
                'template_name': 'Default Followup',
                'subject_line': 'Following up: Debarment monitoring',
                'email_body': '''Hi{greeting},

Just following up on my previous email about debarment monitoring.

This is especially important if you work with subcontractors or have federal contracts.

Let me know if you'd like a quick demo.

Best regards'''
            }
        ]

        for template in sample_templates:
            try:
                models.create_template(**template)
                stats['templates_created'] += 1
            except ValueError:
                # Already exists, skip
                pass
            except Exception as e:
                stats['errors'].append(
                    f"Template {template['template_name']}: {str(e)}"
                )

        return stats

    except Exception as e:
        raise RuntimeError(f"Failed to seed sample data: {str(e)}")


def get_database_stats() -> Dict[str, Any]:
    """
    Get statistics about the database contents.

    Returns:
        Dictionary with database statistics
    """
    try:
        stats = {
            'database_path': schema.get_database_path(),
            'database_exists': schema.database_exists(),
            'database_size_bytes': 0,
            'verticals_count': len(models.get_verticals()),
            'verticals_active': len(models.get_verticals(active_only=True)),
            'accounts_count': len(models.get_email_accounts()),
            'accounts_active': len(models.get_email_accounts(active_only=True)),
            'templates_count': len(models.get_templates()),
            'templates_active': len(models.get_templates(active_only=True)),
            'settings_count': len(models.get_all_settings()),
        }

        # Get database file size
        db_path = schema.get_database_path()
        if os.path.exists(db_path):
            stats['database_size_bytes'] = os.path.getsize(db_path)
            stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)

        return stats

    except Exception as e:
        raise RuntimeError(f"Failed to get database stats: {str(e)}")


def verify_database_integrity() -> Dict[str, Any]:
    """
    Verify database integrity and return a report.

    Returns:
        Dictionary with integrity check results
    """
    try:
        report = {
            'schema_valid': schema.verify_schema(),
            'encryption_working': False,
            'issues': [],
            'warnings': []
        }

        # Test encryption
        try:
            from . import encryption
            report['encryption_working'] = encryption.test_encryption()
        except Exception as e:
            report['issues'].append(f"Encryption test failed: {str(e)}")

        # Check for orphaned assignments (accounts assigned to non-existent verticals)
        try:
            matrix = models.get_assignment_matrix()
            all_verticals = {v['vertical_id'] for v in models.get_verticals()}

            for account_id, vertical_ids in matrix.items():
                for vertical_id in vertical_ids:
                    if vertical_id not in all_verticals:
                        report['warnings'].append(
                            f"Account {account_id} assigned to non-existent vertical '{vertical_id}'"
                        )
        except Exception as e:
            report['issues'].append(f"Failed to check assignments: {str(e)}")

        # Check for templates without verticals
        try:
            templates = models.get_templates()
            all_verticals = {v['vertical_id'] for v in models.get_verticals()}

            for template in templates:
                if template['vertical_id'] not in all_verticals:
                    report['warnings'].append(
                        f"Template {template['template_id']} "
                        f"references non-existent vertical '{template['vertical_id']}'"
                    )
        except Exception as e:
            report['issues'].append(f"Failed to check templates: {str(e)}")

        return report

    except Exception as e:
        raise RuntimeError(f"Failed to verify database integrity: {str(e)}")


if __name__ == "__main__":
    # Test migrations when run directly
    print("Testing database migrations...")

    try:
        # Get stats
        stats = get_database_stats()
        print(f"\nDatabase Stats:")
        print(f"  Path: {stats['database_path']}")
        print(f"  Exists: {stats['database_exists']}")
        print(f"  Verticals: {stats['verticals_count']} ({stats['verticals_active']} active)")
        print(f"  Accounts: {stats['accounts_count']} ({stats['accounts_active']} active)")
        print(f"  Templates: {stats['templates_count']} ({stats['templates_active']} active)")

        # Verify integrity
        integrity = verify_database_integrity()
        print(f"\nIntegrity Check:")
        print(f"  Schema Valid: {integrity['schema_valid']}")
        print(f"  Encryption Working: {integrity['encryption_working']}")
        print(f"  Issues: {len(integrity['issues'])}")
        print(f"  Warnings: {len(integrity['warnings'])}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
