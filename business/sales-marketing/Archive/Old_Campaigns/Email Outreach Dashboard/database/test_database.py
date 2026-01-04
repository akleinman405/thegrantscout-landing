"""
Database Testing Script
Campaign Control Center Dashboard

Comprehensive test suite for all database operations.
Run this script to verify the database layer is working correctly.
"""

import sys
from typing import List, Dict, Any


def test_encryption():
    """Test encryption module."""
    print("\n=== Testing Encryption Module ===")

    from . import encryption

    try:
        # Test encryption/decryption
        test_password = "MySecurePassword123!@#"
        encrypted = encryption.encrypt_password(test_password)
        print(f"✓ Password encrypted: {len(encrypted)} bytes")

        decrypted = encryption.decrypt_password(encrypted)
        assert decrypted == test_password, "Decrypted password doesn't match!"
        print(f"✓ Password decrypted correctly")

        # Test with different password
        another_password = "AnotherPassword456$%^"
        encrypted2 = encryption.encrypt_password(another_password)
        assert encrypted != encrypted2, "Same ciphertext for different passwords!"
        print(f"✓ Different passwords produce different ciphertexts")

        # Test round-trip
        assert encryption.test_encryption(), "Encryption test failed!"
        print(f"✓ Encryption round-trip test passed")

        print("✓ Encryption module: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Encryption module FAILED: {str(e)}\n")
        return False


def test_schema():
    """Test schema module."""
    print("=== Testing Schema Module ===")

    from . import schema

    try:
        # Test database path
        db_path = schema.get_database_path()
        print(f"✓ Database path: {db_path}")

        # Test schema verification
        assert schema.verify_schema(), "Schema verification failed!"
        print(f"✓ Schema verified")

        # Test connection
        conn = schema.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        expected_tables = [
            'verticals', 'email_accounts', 'account_verticals',
            'email_templates', 'campaign_settings'
        ]
        for table in expected_tables:
            assert table in tables, f"Table '{table}' not found!"
        print(f"✓ All {len(expected_tables)} tables exist")

        print("✓ Schema module: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Schema module FAILED: {str(e)}\n")
        return False


def test_verticals():
    """Test vertical CRUD operations."""
    print("=== Testing Verticals CRUD ===")

    from . import models

    try:
        # Create test vertical
        success = models.create_vertical(
            vertical_id='test_vertical',
            display_name='Test Vertical',
            csv_filename='test_prospects.csv',
            target_industry='Testing Industry'
        )
        assert success, "Failed to create vertical"
        print(f"✓ Created vertical 'test_vertical'")

        # Get vertical
        vertical = models.get_vertical('test_vertical')
        assert vertical is not None, "Failed to retrieve vertical"
        assert vertical['display_name'] == 'Test Vertical'
        print(f"✓ Retrieved vertical: {vertical['display_name']}")

        # Update vertical
        success = models.update_vertical(
            'test_vertical',
            display_name='Updated Test Vertical'
        )
        assert success, "Failed to update vertical"
        vertical = models.get_vertical('test_vertical')
        assert vertical['display_name'] == 'Updated Test Vertical'
        print(f"✓ Updated vertical name")

        # List verticals
        verticals = models.get_verticals()
        assert len(verticals) >= 1, "No verticals found"
        print(f"✓ Listed {len(verticals)} vertical(s)")

        # Toggle active
        success = models.toggle_vertical_active('test_vertical', False)
        assert success, "Failed to toggle active status"
        vertical = models.get_vertical('test_vertical')
        assert vertical['active'] == 0
        print(f"✓ Toggled vertical to inactive")

        # Get active only
        active_verticals = models.get_verticals(active_only=True)
        test_in_active = any(v['vertical_id'] == 'test_vertical' for v in active_verticals)
        assert not test_in_active, "Inactive vertical appeared in active list"
        print(f"✓ Active filter works correctly")

        # Delete vertical
        success = models.delete_vertical('test_vertical')
        assert success, "Failed to delete vertical"
        vertical = models.get_vertical('test_vertical')
        assert vertical is None, "Vertical still exists after deletion"
        print(f"✓ Deleted vertical")

        print("✓ Verticals CRUD: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Verticals CRUD FAILED: {str(e)}\n")
        # Cleanup
        try:
            models.delete_vertical('test_vertical')
        except:
            pass
        return False


def test_email_accounts():
    """Test email account CRUD operations."""
    print("=== Testing Email Accounts CRUD ===")

    from . import models

    try:
        # Create test account
        account_id = models.create_email_account(
            email_address='test@example.com',
            smtp_host='smtp.example.com',
            smtp_port=587,
            smtp_username='test@example.com',
            password='TestPassword123!',
            daily_send_limit=450,
            display_name='Test Account'
        )
        assert account_id > 0, "Failed to create account"
        print(f"✓ Created account with ID: {account_id}")

        # Get account
        account = models.get_email_account(account_id)
        assert account is not None, "Failed to retrieve account"
        assert account['email_address'] == 'test@example.com'
        print(f"✓ Retrieved account: {account['email_address']}")

        # Test password decryption
        decrypted_password = models.get_account_password_decrypted(account_id)
        assert decrypted_password == 'TestPassword123!', "Password decryption failed"
        print(f"✓ Password encrypted and decrypted correctly")

        # Update account
        success = models.update_email_account(
            account_id,
            display_name='Updated Test Account',
            daily_send_limit=500
        )
        assert success, "Failed to update account"
        account = models.get_email_account(account_id)
        assert account['display_name'] == 'Updated Test Account'
        assert account['daily_send_limit'] == 500
        print(f"✓ Updated account details")

        # Update password
        success = models.update_email_account(
            account_id,
            password='NewPassword456!'
        )
        assert success, "Failed to update password"
        new_password = models.get_account_password_decrypted(account_id)
        assert new_password == 'NewPassword456!', "New password incorrect"
        print(f"✓ Updated password")

        # List accounts
        accounts = models.get_email_accounts()
        assert len(accounts) >= 1, "No accounts found"
        print(f"✓ Listed {len(accounts)} account(s)")

        # Toggle active
        success = models.toggle_account_active(account_id, False)
        assert success, "Failed to toggle active status"
        print(f"✓ Toggled account to inactive")

        # Delete account
        success = models.delete_email_account(account_id)
        assert success, "Failed to delete account"
        account = models.get_email_account(account_id)
        assert account is None, "Account still exists after deletion"
        print(f"✓ Deleted account")

        print("✓ Email Accounts CRUD: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Email Accounts CRUD FAILED: {str(e)}\n")
        return False


def test_assignments():
    """Test account-vertical assignments."""
    print("=== Testing Account-Vertical Assignments ===")

    from . import models

    try:
        # Create test data
        models.create_vertical(
            'test_vert1', 'Test Vertical 1', 'test1.csv'
        )
        models.create_vertical(
            'test_vert2', 'Test Vertical 2', 'test2.csv'
        )
        account_id = models.create_email_account(
            'assign_test@example.com', 'smtp.example.com', 587,
            'assign_test@example.com', 'Password123!', 450
        )
        print(f"✓ Created test data (2 verticals, 1 account)")

        # Assign account to verticals
        models.assign_account_to_vertical(account_id, 'test_vert1')
        models.assign_account_to_vertical(account_id, 'test_vert2')
        print(f"✓ Assigned account to 2 verticals")

        # Get account's verticals
        verticals = models.get_account_verticals(account_id)
        assert len(verticals) == 2, "Expected 2 verticals"
        assert 'test_vert1' in verticals and 'test_vert2' in verticals
        print(f"✓ Retrieved account's verticals: {verticals}")

        # Get vertical's accounts
        accounts = models.get_vertical_accounts('test_vert1')
        assert len(accounts) >= 1, "Expected at least 1 account"
        assert any(a['account_id'] == account_id for a in accounts)
        print(f"✓ Retrieved vertical's accounts")

        # Get assignment matrix
        matrix = models.get_assignment_matrix()
        assert account_id in matrix, "Account not in matrix"
        assert len(matrix[account_id]) == 2, "Expected 2 assignments in matrix"
        print(f"✓ Assignment matrix: {matrix}")

        # Unassign
        success = models.unassign_account_from_vertical(account_id, 'test_vert1')
        assert success, "Failed to unassign"
        verticals = models.get_account_verticals(account_id)
        assert len(verticals) == 1 and 'test_vert2' in verticals
        print(f"✓ Unassigned account from vertical")

        # Cleanup
        models.delete_email_account(account_id)
        models.delete_vertical('test_vert1')
        models.delete_vertical('test_vert2')
        print(f"✓ Cleaned up test data")

        print("✓ Account-Vertical Assignments: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Account-Vertical Assignments FAILED: {str(e)}\n")
        # Cleanup
        try:
            models.delete_email_account(account_id)
            models.delete_vertical('test_vert1')
            models.delete_vertical('test_vert2')
        except:
            pass
        return False


def test_templates():
    """Test template CRUD operations."""
    print("=== Testing Templates CRUD ===")

    from . import models

    try:
        # Create test vertical
        models.create_vertical(
            'template_test_vert', 'Template Test Vertical', 'template_test.csv'
        )
        print(f"✓ Created test vertical")

        # Create template
        template_id = models.create_template(
            vertical_id='template_test_vert',
            template_type='initial',
            template_name='Test Template',
            subject_line='Test Subject',
            email_body='Test body with {greeting} and {company}'
        )
        assert template_id > 0, "Failed to create template"
        print(f"✓ Created template with ID: {template_id}")

        # Get template
        template = models.get_template(template_id)
        assert template is not None, "Failed to retrieve template"
        assert template['template_name'] == 'Test Template'
        print(f"✓ Retrieved template: {template['template_name']}")

        # Update template
        success = models.update_template(
            template_id,
            subject_line='Updated Subject'
        )
        assert success, "Failed to update template"
        template = models.get_template(template_id)
        assert template['subject_line'] == 'Updated Subject'
        print(f"✓ Updated template")

        # List templates
        templates = models.get_templates(vertical_id='template_test_vert')
        assert len(templates) >= 1, "No templates found"
        print(f"✓ Listed {len(templates)} template(s) for vertical")

        # Filter by type
        initial_templates = models.get_templates(template_type='initial')
        assert len(initial_templates) >= 1, "No initial templates found"
        print(f"✓ Filtered templates by type")

        # Get active template
        active = models.get_active_template('template_test_vert', 'initial')
        assert active is not None, "No active template found"
        print(f"✓ Retrieved active template")

        # Toggle active
        success = models.toggle_template_active(template_id, False)
        assert success, "Failed to toggle active status"
        print(f"✓ Toggled template to inactive")

        # Delete template (cascade test will happen when vertical is deleted)
        success = models.delete_template(template_id)
        assert success, "Failed to delete template"
        print(f"✓ Deleted template")

        # Cleanup
        models.delete_vertical('template_test_vert')
        print(f"✓ Cleaned up test data")

        print("✓ Templates CRUD: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Templates CRUD FAILED: {str(e)}\n")
        # Cleanup
        try:
            models.delete_vertical('template_test_vert')
        except:
            pass
        return False


def test_settings():
    """Test campaign settings."""
    print("=== Testing Campaign Settings ===")

    from . import models

    try:
        # Set setting
        success = models.set_setting('test_setting', 'test_value', 'Test description')
        assert success, "Failed to set setting"
        print(f"✓ Created setting")

        # Get setting
        value = models.get_setting('test_setting')
        assert value == 'test_value', "Setting value incorrect"
        print(f"✓ Retrieved setting: {value}")

        # Update setting
        success = models.set_setting('test_setting', 'updated_value')
        assert success, "Failed to update setting"
        value = models.get_setting('test_setting')
        assert value == 'updated_value', "Updated value incorrect"
        print(f"✓ Updated setting")

        # Get all settings
        all_settings = models.get_all_settings()
        assert 'test_setting' in all_settings, "Setting not in all settings"
        print(f"✓ Retrieved all settings: {len(all_settings)} total")

        # Get with default
        value = models.get_setting('nonexistent_setting', 'default_value')
        assert value == 'default_value', "Default value not returned"
        print(f"✓ Default value returned for nonexistent setting")

        # Delete setting
        success = models.delete_setting('test_setting')
        assert success, "Failed to delete setting"
        value = models.get_setting('test_setting')
        assert value is None, "Setting still exists after deletion"
        print(f"✓ Deleted setting")

        print("✓ Campaign Settings: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Campaign Settings FAILED: {str(e)}\n")
        return False


def test_cascade_delete():
    """Test cascade delete functionality."""
    print("=== Testing Cascade Delete ===")

    from . import models

    try:
        # Create test data
        models.create_vertical('cascade_vert', 'Cascade Test', 'cascade.csv')
        template_id = models.create_template(
            'cascade_vert', 'initial', 'Cascade Template',
            'Subject', 'Body'
        )
        account_id = models.create_email_account(
            'cascade@example.com', 'smtp.example.com', 587,
            'cascade@example.com', 'Password123!', 450
        )
        models.assign_account_to_vertical(account_id, 'cascade_vert')
        print(f"✓ Created test data (vertical, template, account, assignment)")

        # Delete vertical (should cascade to template and assignment)
        success = models.delete_vertical('cascade_vert')
        assert success, "Failed to delete vertical"
        print(f"✓ Deleted vertical")

        # Verify template was deleted
        template = models.get_template(template_id)
        assert template is None, "Template not deleted on cascade"
        print(f"✓ Template deleted on cascade")

        # Verify assignment was deleted
        verticals = models.get_account_verticals(account_id)
        assert 'cascade_vert' not in verticals, "Assignment not deleted on cascade"
        print(f"✓ Assignment deleted on cascade")

        # Cleanup
        models.delete_email_account(account_id)
        print(f"✓ Cleaned up test data")

        print("✓ Cascade Delete: PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Cascade Delete FAILED: {str(e)}\n")
        return False


def run_all_tests():
    """Run all database tests."""
    print("\n" + "="*60)
    print("DATABASE TEST SUITE")
    print("Campaign Control Center Dashboard")
    print("="*60)

    # Initialize database first
    from . import schema
    if not schema.database_exists():
        print("\nInitializing database...")
        schema.init_database()
        print("✓ Database initialized\n")

    results = []

    # Run tests (Encryption first, then Schema which will initialize)
    results.append(("Encryption", test_encryption()))

    # Initialize database before schema test
    from . import schema
    schema.init_database()

    results.append(("Schema", test_schema()))
    results.append(("Verticals CRUD", test_verticals()))
    results.append(("Email Accounts CRUD", test_email_accounts()))
    results.append(("Account-Vertical Assignments", test_assignments()))
    results.append(("Templates CRUD", test_templates()))
    results.append(("Campaign Settings", test_settings()))
    results.append(("Cascade Delete", test_cascade_delete()))

    # Print summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:.<45} {status}")

    print("="*60)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
