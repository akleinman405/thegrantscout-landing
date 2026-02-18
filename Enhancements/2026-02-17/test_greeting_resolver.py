#!/usr/bin/env python3
"""test_greeting_resolver.py - Unit tests for greeting_resolver module.

Covers all edge cases including the 7 Kathleen cases from the 2026-02-18 audit.

Usage:
    python3 test_greeting_resolver.py
"""

import sys
import unittest
from greeting_resolver import resolve_greeting, format_greeting_line


class TestResolveGreeting(unittest.TestCase):
    """Test resolve_greeting() logic."""

    # --- Generic inbox tests ---

    def test_generic_inbox_info(self):
        name, reason = resolve_greeting("Kathleen", "info@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_inbox_admin(self):
        name, reason = resolve_greeting("John", "admin@example.org")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_inbox_office(self):
        name, reason = resolve_greeting("Susan", "office@nonprofit.org")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_compound_front_desk(self):
        name, reason = resolve_greeting("Lars", "front-desk@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_department_boxoffice(self):
        name, reason = resolve_greeting("Nancy", "boxoffice@theater.org")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_pattern_contact_us(self):
        name, reason = resolve_greeting("Bill", "contact-us@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_pattern_noreply(self):
        name, reason = resolve_greeting("Alice", "noreply@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_pattern_do_not_reply(self):
        name, reason = resolve_greeting("Mike", "do-not-reply@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_pattern_ends_with_office(self):
        name, reason = resolve_greeting("Lars", "wa-office@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_pattern_ends_with_admin(self):
        name, reason = resolve_greeting("John", "fladmin@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_long_prefix(self):
        name, reason = resolve_greeting("John", "waldenacademy.org_1e0abc@example.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_member_prefix(self):
        name, reason = resolve_greeting("Tom", "member-services@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    # --- Exact match tests ---

    def test_exact_match_simple(self):
        name, reason = resolve_greeting("Nancy", "nancy@wayneart.org")
        self.assertEqual(name, "Nancy")
        self.assertEqual(reason, "exact_match")

    def test_exact_match_firstname_lastname(self):
        name, reason = resolve_greeting("Scott", "scott.lloyd@org.com")
        self.assertEqual(name, "Scott")
        self.assertEqual(reason, "exact_match")

    def test_exact_match_firstname_underscore(self):
        name, reason = resolve_greeting("Jane", "jane_doe@org.com")
        self.assertEqual(name, "Jane")
        self.assertEqual(reason, "exact_match")

    def test_exact_match_firstname_dash(self):
        name, reason = resolve_greeting("Mary", "mary-jones@org.com")
        self.assertEqual(name, "Mary")
        self.assertEqual(reason, "exact_match")

    # --- Nickname match tests ---

    def test_nickname_forward_pamela_pam(self):
        name, reason = resolve_greeting("Pamela", "pam@org.com")
        self.assertEqual(name, "Pam")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_forward_william_bill(self):
        name, reason = resolve_greeting("William", "bill@org.com")
        self.assertEqual(name, "Bill")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_forward_elizabeth_beth(self):
        name, reason = resolve_greeting("Elizabeth", "beth@org.com")
        self.assertEqual(name, "Beth")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_reverse_steve_steven(self):
        name, reason = resolve_greeting("Steve", "steven@org.com")
        self.assertEqual(name, "Steven")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_reverse_mike_michael(self):
        name, reason = resolve_greeting("Mike", "michael@org.com")
        self.assertEqual(name, "Michael")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_reverse_bob_robert(self):
        name, reason = resolve_greeting("Bob", "robert@org.com")
        self.assertEqual(name, "Robert")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_katherine_kate(self):
        name, reason = resolve_greeting("Katherine", "kate@org.com")
        self.assertEqual(name, "Kate")
        self.assertEqual(reason, "nickname_match")

    def test_nickname_kathleen_kathy(self):
        name, reason = resolve_greeting("Kathleen", "kathy@org.com")
        self.assertEqual(name, "Kathy")
        self.assertEqual(reason, "nickname_match")

    # --- Initial only tests ---

    def test_initial_only(self):
        name, reason = resolve_greeting("Sam", "j.severson@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "initial_only")

    def test_initial_only_single_letter(self):
        name, reason = resolve_greeting("Thomas", "t.smith@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "initial_only")

    # --- No match tests ---

    def test_no_match_different_name(self):
        name, reason = resolve_greeting("Kathleen", "lqualls@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "no_match")

    def test_no_match_different_person(self):
        name, reason = resolve_greeting("John", "jennifer.smith@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "no_match")

    def test_no_match_surname_only(self):
        name, reason = resolve_greeting("Sarah", "johnson@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "no_match")

    # --- Junk email tests ---

    def test_junk_google_calendar(self):
        name, reason = resolve_greeting("Bill", "abc123@group.calendar.google.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "junk_email")

    def test_junk_webp_extension(self):
        name, reason = resolve_greeting("Jane", "image.webp@fake.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "junk_email")

    # --- Placeholder name tests ---

    def test_placeholder_there(self):
        name, reason = resolve_greeting("there", "info@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "placeholder_name")

    def test_placeholder_hello(self):
        name, reason = resolve_greeting("Hello", "admin@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "placeholder_name")

    def test_placeholder_team(self):
        name, reason = resolve_greeting("Team", "team@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "placeholder_name")

    def test_placeholder_empty(self):
        name, reason = resolve_greeting("", "info@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "placeholder_name")

    def test_placeholder_none(self):
        name, reason = resolve_greeting(None, "info@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "placeholder_name")

    # --- No email tests ---

    def test_no_email_none(self):
        name, reason = resolve_greeting("John", None)
        self.assertIsNone(name)
        self.assertEqual(reason, "no_email")

    def test_no_email_empty(self):
        name, reason = resolve_greeting("John", "")
        self.assertIsNone(name)
        self.assertEqual(reason, "no_email")

    # --- The 7 Kathleen cases from audit ---
    # All should return (None, ...) so greeting is "Hello,"

    def test_kathleen_case_1_info_inbox(self):
        """Kathleen + info@org = generic inbox."""
        name, reason = resolve_greeting("Kathleen", "info@example.org")
        self.assertIsNone(name)

    def test_kathleen_case_2_office_inbox(self):
        """Kathleen + office@org = generic inbox."""
        name, reason = resolve_greeting("Kathleen", "office@example.org")
        self.assertIsNone(name)

    def test_kathleen_case_3_different_person(self):
        """Kathleen + lqualls@org = no match (different person's email)."""
        name, reason = resolve_greeting("Kathleen", "lqualls@example.org")
        self.assertIsNone(name)

    def test_kathleen_case_4_admin_inbox(self):
        """Kathleen + admin@org = generic inbox."""
        name, reason = resolve_greeting("Kathleen", "admin@example.org")
        self.assertIsNone(name)

    def test_kathleen_case_5_contact_inbox(self):
        """Kathleen + contact@org = generic inbox."""
        name, reason = resolve_greeting("Kathleen", "contact@example.org")
        self.assertIsNone(name)

    def test_kathleen_case_6_general_inbox(self):
        """Kathleen + general@org = generic inbox."""
        name, reason = resolve_greeting("Kathleen", "general@example.org")
        self.assertIsNone(name)

    def test_kathleen_case_7_programs_inbox(self):
        """Kathleen + programs@org = generic inbox."""
        name, reason = resolve_greeting("Kathleen", "programs@example.org")
        self.assertIsNone(name)


class TestFormatGreetingLine(unittest.TestCase):
    """Test format_greeting_line() output."""

    def test_with_name(self):
        self.assertEqual(format_greeting_line("Nancy"), "Hi Nancy,")

    def test_with_none(self):
        self.assertEqual(format_greeting_line(None), "Hello,")

    def test_with_empty_string(self):
        self.assertEqual(format_greeting_line(""), "Hello,")

    def test_with_nickname(self):
        self.assertEqual(format_greeting_line("Pam"), "Hi Pam,")


class TestEdgeCases(unittest.TestCase):
    """Additional edge cases."""

    def test_case_insensitive_email(self):
        """Email matching should be case-insensitive."""
        name, reason = resolve_greeting("Nancy", "Nancy@org.com")
        self.assertEqual(name, "Nancy")
        self.assertEqual(reason, "exact_match")

    def test_all_caps_officer_name(self):
        """ALL CAPS officer name should be normalized to title case."""
        name, reason = resolve_greeting("NANCY", "nancy@org.com")
        self.assertEqual(name, "Nancy")
        self.assertEqual(reason, "exact_match")

    def test_lowercase_officer_name(self):
        """Lowercase officer name should be normalized to title case."""
        name, reason = resolve_greeting("nancy", "nancy@org.com")
        self.assertEqual(name, "Nancy")
        self.assertEqual(reason, "exact_match")

    def test_whitespace_handling(self):
        """Whitespace in inputs should be handled."""
        name, reason = resolve_greeting("  Nancy  ", "  nancy@org.com  ")
        self.assertEqual(name, "Nancy")
        self.assertEqual(reason, "exact_match")

    def test_generic_donations(self):
        name, reason = resolve_greeting("Sue", "donations@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_generic_events(self):
        name, reason = resolve_greeting("Tom", "events@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_nickname_chris_christopher(self):
        name, reason = resolve_greeting("Christopher", "chris@org.com")
        self.assertEqual(name, "Chris")
        self.assertEqual(reason, "nickname_match")

    def test_no_match_bookstore(self):
        """Org-name-based email prefixes should not match."""
        name, reason = resolve_greeting("Maria", "bookstore@library.org")
        self.assertIsNone(name)
        self.assertEqual(reason, "no_match")

    def test_info_dot_something(self):
        """info.something@ should be caught by pattern."""
        name, reason = resolve_greeting("John", "info.request@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_public_affairs(self):
        """public-affairs@ should be caught by pattern."""
        name, reason = resolve_greeting("Tom", "public-affairs@org.com")
        self.assertIsNone(name)
        self.assertEqual(reason, "generic_inbox")

    def test_nickname_samantha_sam(self):
        """Samantha -> Sam nickname should match."""
        name, reason = resolve_greeting("Samantha", "sam@org.com")
        self.assertEqual(name, "Sam")
        self.assertEqual(reason, "nickname_match")

    def test_format_preserves_capitalization(self):
        """format_greeting_line should output proper casing."""
        self.assertEqual(format_greeting_line("Nancy"), "Hi Nancy,")
        # Even if someone passes weird casing, it passes through
        self.assertEqual(format_greeting_line("NANCY"), "Hi NANCY,")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    sys.exit(0 if result.result.wasSuccessful() else 1)
