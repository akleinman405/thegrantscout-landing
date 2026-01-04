"""
Quality checklist for generated reports.
Run manually on generated reports.
"""

from pathlib import Path
import re
import sys


def check_report_quality(md_path: str) -> dict:
    """
    Run quality checks on a generated report.

    Returns dict with check results.
    """
    with open(md_path, encoding='utf-8') as f:
        content = f.read()

    results = {}

    # 1. Has all required sections
    required_sections = [
        ("Header", r"^# .+"),
        ("One Thing", r"## If You Only Do One Thing"),
        ("Executive Summary", r"## Executive Summary"),
        ("Top 5 Table", r"## Top 5 Opportunities"),
        ("Opportunity 1", r"## Opportunity #1"),
        ("Timeline", r"## 8-Week Timeline"),
        ("Quick Reference", r"## Quick Reference")
    ]

    for name, pattern in required_sections:
        results[f"section_{name}"] = bool(re.search(pattern, content, re.MULTILINE))

    # 2. No unfilled placeholders
    placeholders = re.findall(r'\{[a-z_]+\}', content)
    results["no_placeholders"] = len(placeholders) == 0
    results["placeholder_count"] = len(placeholders)
    if placeholders:
        results["placeholders_found"] = placeholders[:5]  # First 5

    # 3. Tables are formatted
    results["tables_formatted"] = "|---|" in content

    # 4. Dollar amounts formatted
    dollar_amounts = re.findall(r'\$[\d,]+', content)
    results["has_dollar_amounts"] = len(dollar_amounts) > 0
    results["dollar_amount_count"] = len(dollar_amounts)

    # 5. Dates present
    dates = re.findall(r'\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4}', content)
    results["has_dates"] = len(dates) > 0
    results["date_count"] = len(dates)

    # 6. Length check
    results["content_length"] = len(content)
    results["reasonable_length"] = 5000 < len(content) < 50000

    # 7. No error messages in content
    error_patterns = ["Traceback", "Exception:", "Error:"]
    results["no_errors"] = not any(p in content for p in error_patterns)

    # 8. Has foundation names
    results["has_foundation_names"] = "Foundation" in content or "Fund" in content

    # 9. Has narrative content
    results["has_why_this_fits"] = "Why This Fits" in content
    results["has_positioning"] = "Positioning Strategy" in content
    results["has_next_steps"] = "Next Steps" in content

    # 10. Count opportunities
    opp_count = len(re.findall(r'## Opportunity #\d', content))
    results["opportunity_count"] = opp_count
    results["has_5_opportunities"] = opp_count >= 5

    return results


def print_quality_report(results: dict):
    """Print formatted quality report."""
    print("\n" + "=" * 60)
    print("QUALITY CHECK RESULTS")
    print("=" * 60)

    passed = 0
    failed = 0

    for check, result in results.items():
        if isinstance(result, bool):
            status = "PASS" if result else "FAIL"
            color_start = "" if result else ""
            if result:
                passed += 1
            else:
                failed += 1
            print(f"[{status}] {check}")
        else:
            print(f"      {check}: {result}")

    print("=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quality_checklist.py <report.md>")
        sys.exit(1)

    md_path = sys.argv[1]

    if not Path(md_path).exists():
        print(f"File not found: {md_path}")
        sys.exit(1)

    results = check_report_quality(md_path)
    success = print_quality_report(results)

    sys.exit(0 if success else 1)
