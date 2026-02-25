#!/usr/bin/env python3
"""
Contact Verification Module for Grant Reports (Pipeline Step 09)

Verifies foundation contact information before report delivery.
Three verification layers:
  Layer 1: MX record check (domain accepts mail)
  Layer 2: SMTP handshake verification (mailbox exists, no email sent)
  Layer 3: URL liveness check (website/portal responds)

Usage:
    # Verify a single email
    python 09_contact_verification.py email elizabeth.burdette@signaturefd.com

    # Verify a URL
    python 09_contact_verification.py url https://billsimpsonfoundation.org

    # Verify contacts from a JSON file
    python 09_contact_verification.py batch contacts.json

    # Verify contacts from a report markdown file
    python 09_contact_verification.py report path/to/report.md

Output:
    JSON results file + human-readable console summary
"""

import argparse
import json
import re
import smtplib
import socket
import ssl
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import dns.resolver
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

SMTP_TIMEOUT = 15          # seconds per connection attempt
SMTP_RETRY_DELAY = 30     # seconds before retry on greylisting
SMTP_MAX_RETRIES = 1      # retry once on temporary failure
URL_TIMEOUT = 15           # seconds for HTTP requests
VERIFY_FROM = "verify@thegrantscout.com"  # MAIL FROM address for SMTP check

# Status constants
STATUS_VERIFIED = "VERIFIED"
STATUS_FAIL = "FAIL"
STATUS_INCONCLUSIVE = "INCONCLUSIVE"
STATUS_ERROR = "ERROR"
STATUS_PASS = "PASS"
STATUS_WARN = "WARN"
STATUS_CATCH_ALL = "CATCH_ALL"

# Common catch-all indicators
CATCH_ALL_CODES = {252, 250}  # 252 = cannot verify, 250 might be catch-all

# User-Agent for URL checks
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ============================================================================
# LAYER 1: MX RECORD CHECK
# ============================================================================

def check_mx(domain: str) -> Dict:
    """
    Check if a domain has valid MX records.

    Returns:
        {
            "status": "PASS" | "FAIL" | "WARN",
            "mx_records": ["mx1.example.com", ...],
            "detail": "description"
        }
    """
    result = {
        "status": STATUS_ERROR,
        "mx_records": [],
        "detail": ""
    }

    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_records = sorted(
            [(r.preference, str(r.exchange).rstrip(".")) for r in answers],
            key=lambda x: x[0]
        )
        result["mx_records"] = [mx for _, mx in mx_records]

        if mx_records:
            result["status"] = STATUS_PASS
            result["detail"] = f"{len(mx_records)} MX record(s) found"
        else:
            result["status"] = STATUS_FAIL
            result["detail"] = "No MX records found"

    except dns.resolver.NXDOMAIN:
        result["status"] = STATUS_FAIL
        result["detail"] = f"Domain {domain} does not exist (NXDOMAIN)"

    except dns.resolver.NoAnswer:
        # No MX records, but domain exists. Check for A record fallback.
        try:
            dns.resolver.resolve(domain, "A")
            result["status"] = STATUS_WARN
            result["detail"] = "No MX records, but A record exists (may accept mail)"
        except Exception:
            result["status"] = STATUS_FAIL
            result["detail"] = "No MX or A records found"

    except dns.resolver.NoNameservers:
        result["status"] = STATUS_FAIL
        result["detail"] = "No nameservers found for domain"

    except dns.resolver.Timeout:
        result["status"] = STATUS_ERROR
        result["detail"] = "DNS query timed out"

    except Exception as e:
        result["status"] = STATUS_ERROR
        result["detail"] = f"DNS error: {str(e)}"

    return result


# ============================================================================
# LAYER 2: SMTP HANDSHAKE VERIFICATION
# ============================================================================

def _smtp_handshake(email: str, mx_host: str, attempt: int = 1) -> Dict:
    """
    Perform SMTP handshake to verify mailbox exists.
    Does NOT send any email.

    Steps: EHLO -> MAIL FROM -> RCPT TO -> check response -> QUIT
    """
    result = {
        "status": STATUS_ERROR,
        "smtp_code": None,
        "detail": "",
        "mx_used": mx_host,
        "attempt": attempt
    }

    try:
        # Connect to mail server
        server = smtplib.SMTP(mx_host, 25, timeout=SMTP_TIMEOUT)

        # EHLO
        code, msg = server.ehlo("thegrantscout.com")
        if code != 250:
            result["detail"] = f"EHLO rejected: {code} {msg.decode('utf-8', errors='replace')}"
            server.quit()
            return result

        # Try STARTTLS if available (some servers require it)
        try:
            if server.has_extn("STARTTLS"):
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                server.starttls(context=context)
                server.ehlo("thegrantscout.com")
        except (smtplib.SMTPException, ssl.SSLError, OSError):
            # STARTTLS failed, reconnect without TLS
            try:
                server.close()
            except Exception:
                pass
            server = smtplib.SMTP(mx_host, 25, timeout=SMTP_TIMEOUT)
            server.ehlo("thegrantscout.com")

        # MAIL FROM
        code, msg = server.mail(VERIFY_FROM)
        if code != 250:
            result["detail"] = f"MAIL FROM rejected: {code} {msg.decode('utf-8', errors='replace')}"
            result["smtp_code"] = code
            server.quit()
            return result

        # RCPT TO - this is the key check
        code, msg = server.rcpt(email)
        result["smtp_code"] = code
        msg_str = msg.decode("utf-8", errors="replace")

        if code == 250:
            # Check for catch-all by testing a random address
            fake_email = f"nonexistent-verify-{int(time.time())}@{email.split('@')[1]}"
            fake_code, _ = server.rcpt(fake_email)

            if fake_code == 250:
                result["status"] = STATUS_CATCH_ALL
                result["detail"] = f"Server accepts all addresses (catch-all). Real check inconclusive."
            else:
                result["status"] = STATUS_VERIFIED
                result["detail"] = f"250 {msg_str}"

        elif code in (550, 551, 553):
            # Check if this is a blocklist rejection (not a real mailbox failure)
            blocklist_keywords = ["spamhaus", "blocked", "blacklist", "blocklist",
                                  "barracuda", "sorbs", "uceprotect", "dnsbl"]
            msg_lower = msg_str.lower()
            if any(kw in msg_lower for kw in blocklist_keywords):
                result["status"] = STATUS_INCONCLUSIVE
                result["detail"] = f"IP blocklisted ({code}): {msg_str}"
            else:
                result["status"] = STATUS_FAIL
                result["detail"] = f"{code} {msg_str}"

        elif code in (450, 451, 452):
            # Temporary failure - might be greylisting
            result["status"] = STATUS_INCONCLUSIVE
            result["detail"] = f"Temporary rejection ({code}): {msg_str}"

        elif code == 252:
            result["status"] = STATUS_INCONCLUSIVE
            result["detail"] = f"Cannot verify (252): {msg_str}"

        else:
            result["status"] = STATUS_INCONCLUSIVE
            result["detail"] = f"Unexpected code {code}: {msg_str}"

        server.quit()

    except smtplib.SMTPServerDisconnected:
        result["status"] = STATUS_ERROR
        result["detail"] = "Server disconnected unexpectedly"

    except smtplib.SMTPConnectError as e:
        result["status"] = STATUS_ERROR
        result["detail"] = f"Connection refused: {str(e)}"

    except socket.timeout:
        result["status"] = STATUS_ERROR
        result["detail"] = f"Connection timed out after {SMTP_TIMEOUT}s"

    except ConnectionRefusedError:
        result["status"] = STATUS_ERROR
        result["detail"] = "Connection refused on port 25"

    except OSError as e:
        result["status"] = STATUS_ERROR
        result["detail"] = f"Network error: {str(e)}"

    except Exception as e:
        result["status"] = STATUS_ERROR
        result["detail"] = f"SMTP error: {type(e).__name__}: {str(e)}"

    return result


def verify_email_smtp(email: str, mx_records: Optional[List[str]] = None) -> Dict:
    """
    Full SMTP verification of an email address.
    Tries each MX record in priority order.
    Retries once on greylisting/temporary failures.
    """
    domain = email.split("@")[1]

    # Get MX records if not provided
    if not mx_records:
        mx_result = check_mx(domain)
        mx_records = mx_result.get("mx_records", [])
        if not mx_records:
            return {
                "status": STATUS_ERROR,
                "smtp_code": None,
                "detail": f"No MX records for {domain}",
                "mx_used": None,
                "attempt": 0
            }

    # Try each MX host
    last_result = None
    for mx_host in mx_records[:3]:  # Try top 3 MX records
        result = _smtp_handshake(email, mx_host)

        if result["status"] == STATUS_VERIFIED:
            return result

        if result["status"] == STATUS_FAIL:
            return result

        if result["status"] == STATUS_CATCH_ALL:
            return result

        # On temporary/inconclusive, retry once after delay
        if result["status"] == STATUS_INCONCLUSIVE and SMTP_MAX_RETRIES > 0:
            time.sleep(SMTP_RETRY_DELAY)
            retry_result = _smtp_handshake(email, mx_host, attempt=2)
            if retry_result["status"] in (STATUS_VERIFIED, STATUS_FAIL, STATUS_CATCH_ALL):
                return retry_result
            result = retry_result

        last_result = result

    return last_result or {
        "status": STATUS_ERROR,
        "smtp_code": None,
        "detail": "All MX hosts failed",
        "mx_used": None,
        "attempt": 0
    }


# ============================================================================
# LAYER 3: URL LIVENESS CHECK
# ============================================================================

def check_url(url: str) -> Dict:
    """
    Check if a URL is live and responding.

    Returns:
        {
            "status": "PASS" | "FAIL" | "WARN",
            "http_code": 200,
            "final_url": "https://...",
            "detail": "description"
        }
    """
    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {
        "status": STATUS_ERROR,
        "http_code": None,
        "final_url": None,
        "detail": "",
        "url_checked": url
    }

    headers = {"User-Agent": USER_AGENT}

    try:
        # Try HEAD first (lighter)
        resp = requests.head(
            url,
            timeout=URL_TIMEOUT,
            allow_redirects=True,
            headers=headers,
            verify=True
        )

        # Some servers reject HEAD, fall back to GET
        if resp.status_code in (405, 403, 400):
            resp = requests.get(
                url,
                timeout=URL_TIMEOUT,
                allow_redirects=True,
                headers=headers,
                verify=True
            )

        result["http_code"] = resp.status_code
        result["final_url"] = resp.url

        if resp.status_code == 200:
            result["status"] = STATUS_PASS
            result["detail"] = "200 OK"
        elif 300 <= resp.status_code < 400:
            result["status"] = STATUS_PASS
            result["detail"] = f"Redirect to {resp.url}"
        elif resp.status_code == 403:
            result["status"] = STATUS_WARN
            result["detail"] = "403 Forbidden (site exists but blocks automated checks)"
        elif resp.status_code == 404:
            result["status"] = STATUS_FAIL
            result["detail"] = "404 Not Found"
        elif resp.status_code == 503:
            result["status"] = STATUS_WARN
            result["detail"] = "503 Service Unavailable (temporary)"
        else:
            result["status"] = STATUS_WARN
            result["detail"] = f"HTTP {resp.status_code}"

    except requests.exceptions.SSLError:
        # Try without SSL verification
        try:
            resp = requests.get(
                url, timeout=URL_TIMEOUT, allow_redirects=True,
                headers=headers, verify=False
            )
            result["http_code"] = resp.status_code
            result["final_url"] = resp.url
            result["status"] = STATUS_WARN
            result["detail"] = f"SSL certificate invalid, but site responds ({resp.status_code})"
        except Exception:
            result["status"] = STATUS_FAIL
            result["detail"] = "SSL error and site unreachable"

    except requests.exceptions.ConnectionError:
        result["status"] = STATUS_FAIL
        result["detail"] = "Connection refused or DNS resolution failed"

    except requests.exceptions.Timeout:
        result["status"] = STATUS_FAIL
        result["detail"] = f"Timed out after {URL_TIMEOUT}s"

    except requests.exceptions.TooManyRedirects:
        result["status"] = STATUS_FAIL
        result["detail"] = "Too many redirects"

    except Exception as e:
        result["status"] = STATUS_ERROR
        result["detail"] = f"Error: {type(e).__name__}: {str(e)}"

    return result


# ============================================================================
# FULL CONTACT VERIFICATION
# ============================================================================

def verify_contact(contact: Dict) -> Dict:
    """
    Run all verification layers on a single contact entry.

    Input contact dict:
        {
            "foundation": "Bill Simpson Foundation",
            "emails": ["elizabeth.burdette@signaturefd.com"],
            "phones": ["(404) 473-4924"],
            "urls": ["billsimpsonfoundation.org"]
        }

    Returns full verification results.
    """
    foundation = contact.get("foundation", "Unknown")
    now = datetime.now(timezone.utc).isoformat()

    result = {
        "foundation": foundation,
        "verified_at": now,
        "emails": [],
        "urls": [],
        "phones": contact.get("phones", []),
        "overall_status": STATUS_PASS
    }

    # Verify emails
    for email in contact.get("emails", []):
        email = email.strip().lower()
        domain = email.split("@")[1] if "@" in email else ""

        email_result = {
            "email": email,
            "mx_check": {},
            "smtp_verify": {},
            "verified_at": now
        }

        # Layer 1: MX check
        mx = check_mx(domain)
        email_result["mx_check"] = mx

        # Layer 2: SMTP verification (only if MX passes)
        if mx["status"] in (STATUS_PASS, STATUS_WARN):
            smtp = verify_email_smtp(email, mx.get("mx_records"))
            email_result["smtp_verify"] = smtp
        else:
            email_result["smtp_verify"] = {
                "status": STATUS_ERROR,
                "detail": "Skipped: MX check failed"
            }

        # Roll up status
        smtp_status = email_result["smtp_verify"].get("status", STATUS_ERROR)
        if smtp_status in (STATUS_FAIL,):
            result["overall_status"] = STATUS_FAIL
        elif smtp_status in (STATUS_ERROR, STATUS_INCONCLUSIVE) and result["overall_status"] != STATUS_FAIL:
            result["overall_status"] = STATUS_WARN

        result["emails"].append(email_result)

    # Verify URLs
    for url in contact.get("urls", []):
        url_result = check_url(url)
        result["urls"].append(url_result)

        if url_result["status"] == STATUS_FAIL and result["overall_status"] != STATUS_FAIL:
            result["overall_status"] = STATUS_WARN

    return result


def verify_batch(contacts: List[Dict], output_path: Optional[str] = None) -> Dict:
    """
    Verify a batch of contacts and produce JSON output + console summary.
    """
    results = {
        "verification_run": {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "total_contacts": len(contacts),
            "tool_version": "1.0.0"
        },
        "contacts": []
    }

    for i, contact in enumerate(contacts, 1):
        foundation = contact.get("foundation", "Unknown")
        print(f"\n[{i}/{len(contacts)}] Verifying: {foundation}")
        print("-" * 50)

        result = verify_contact(contact)
        results["contacts"].append(result)

        # Print per-contact summary
        _print_contact_summary(result)

    results["verification_run"]["completed_at"] = datetime.now(timezone.utc).isoformat()

    # Count statuses
    statuses = [c["overall_status"] for c in results["contacts"]]
    results["verification_run"]["summary"] = {
        "pass": statuses.count(STATUS_PASS),
        "warn": statuses.count(STATUS_WARN),
        "fail": statuses.count(STATUS_FAIL)
    }

    # Save JSON
    if output_path:
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to: {output_path}")

    # Print overall summary
    _print_batch_summary(results)

    return results


def _print_contact_summary(result: Dict):
    """Print a human-readable summary for one contact."""
    status_symbols = {
        STATUS_VERIFIED: "[OK]",
        STATUS_PASS: "[OK]",
        STATUS_WARN: "[??]",
        STATUS_FAIL: "[XX]",
        STATUS_ERROR: "[!!]",
        STATUS_INCONCLUSIVE: "[??]",
        STATUS_CATCH_ALL: "[~~]"
    }

    for er in result.get("emails", []):
        mx_status = er["mx_check"].get("status", "?")
        smtp_status = er["smtp_verify"].get("status", "?")
        smtp_detail = er["smtp_verify"].get("detail", "")
        mx_sym = status_symbols.get(mx_status, "[??]")
        smtp_sym = status_symbols.get(smtp_status, "[??]")
        print(f"  Email: {er['email']}")
        print(f"    MX:   {mx_sym} {mx_status} - {er['mx_check'].get('detail', '')}")
        print(f"    SMTP: {smtp_sym} {smtp_status} - {smtp_detail}")

    for ur in result.get("urls", []):
        url_status = ur.get("status", "?")
        url_sym = status_symbols.get(url_status, "[??]")
        print(f"  URL:  {ur.get('url_checked', '?')}")
        print(f"    HTTP: {url_sym} {url_status} - {ur.get('detail', '')}")

    for phone in result.get("phones", []):
        print(f"  Phone: {phone} (manual verification required)")


def _print_batch_summary(results: Dict):
    """Print overall batch summary."""
    summary = results["verification_run"]["summary"]
    total = results["verification_run"]["total_contacts"]

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total contacts: {total}")
    print(f"  PASS: {summary['pass']}")
    print(f"  WARN: {summary['warn']}")
    print(f"  FAIL: {summary['fail']}")

    # List any failures
    failures = [c for c in results["contacts"] if c["overall_status"] == STATUS_FAIL]
    if failures:
        print(f"\nFAILED contacts ({len(failures)}):")
        for f in failures:
            print(f"  - {f['foundation']}")
            for er in f.get("emails", []):
                if er["smtp_verify"].get("status") == STATUS_FAIL:
                    print(f"    Email FAIL: {er['email']} - {er['smtp_verify'].get('detail', '')}")
            for ur in f.get("urls", []):
                if ur.get("status") == STATUS_FAIL:
                    print(f"    URL FAIL: {ur.get('url_checked', '?')} - {ur.get('detail', '')}")


# ============================================================================
# REPORT PARSER
# ============================================================================

def extract_contacts_from_report(report_path: str) -> List[Dict]:
    """
    Extract foundation contacts from a grant report markdown file.
    Looks for email addresses, phone numbers, and URLs in contact tables.
    """
    with open(report_path, "r") as f:
        content = f.read()

    contacts = []
    # Split by foundation profile sections
    sections = re.split(r"###\s+#\d+:\s+", content)

    for section in sections[1:]:  # Skip header
        # Get foundation name (first line)
        name_match = re.match(r"(.+?)(?:\n|$)", section)
        foundation_name = name_match.group(1).strip() if name_match else "Unknown"

        # Extract emails
        emails = list(set(re.findall(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            section
        )))
        # Filter out common false positives
        emails = [e for e in emails if not e.startswith("verify@")]

        # Extract phone numbers
        phones = list(set(re.findall(
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            section
        )))

        # Extract URLs (from markdown links and plain text)
        urls = list(set(re.findall(
            r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.(?:org|com|net|edu))',
            section
        )))
        # Filter out generic URLs
        urls = [u for u in urls if u not in (
            "thegrantscout.com", "calendly.com", "linkedin.com",
            "yourcausegrants.com"
        )]

        if emails or urls:
            contacts.append({
                "foundation": foundation_name,
                "emails": emails,
                "phones": phones,
                "urls": urls
            })

    return contacts


# ============================================================================
# CLI COMMANDS
# ============================================================================

def cmd_email(args):
    """Verify a single email address."""
    email = args.email
    domain = email.split("@")[1]

    print(f"Verifying: {email}")
    print("=" * 50)

    print(f"\n[1/2] MX Check for {domain}...")
    mx = check_mx(domain)
    print(f"  Status: {mx['status']}")
    print(f"  Detail: {mx['detail']}")
    if mx["mx_records"]:
        print(f"  Records: {', '.join(mx['mx_records'][:3])}")

    print(f"\n[2/2] SMTP Verification...")
    if mx["status"] in (STATUS_PASS, STATUS_WARN):
        smtp = verify_email_smtp(email, mx.get("mx_records"))
        print(f"  Status: {smtp['status']}")
        print(f"  Code:   {smtp.get('smtp_code', 'N/A')}")
        print(f"  Detail: {smtp['detail']}")
        if smtp.get("mx_used"):
            print(f"  MX Used: {smtp['mx_used']}")
    else:
        print(f"  Skipped: MX check failed")

    print("\n" + "=" * 50)


def cmd_url(args):
    """Verify a single URL."""
    url = args.url
    print(f"Checking URL: {url}")
    print("=" * 50)

    result = check_url(url)
    print(f"  Status:    {result['status']}")
    print(f"  HTTP Code: {result.get('http_code', 'N/A')}")
    print(f"  Final URL: {result.get('final_url', 'N/A')}")
    print(f"  Detail:    {result['detail']}")


def cmd_batch(args):
    """Verify contacts from a JSON file."""
    with open(args.input, "r") as f:
        contacts = json.load(f)

    verify_batch(contacts, output_path=args.output)


def cmd_report(args):
    """Extract contacts from a report and verify them."""
    print(f"Extracting contacts from: {args.report}")
    contacts = extract_contacts_from_report(args.report)

    if not contacts:
        print("No contacts found in report.")
        return

    print(f"Found {len(contacts)} foundations with contacts")
    for c in contacts:
        print(f"  - {c['foundation']}: {len(c['emails'])} emails, {len(c['urls'])} URLs")

    verify_batch(contacts, output_path=args.output)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Contact Verification for Grant Reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python 09_contact_verification.py email elizabeth.burdette@signaturefd.com
    python 09_contact_verification.py url https://billsimpsonfoundation.org
    python 09_contact_verification.py batch contacts.json -o results.json
    python 09_contact_verification.py report path/to/report.md -o results.json
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # email command
    email_parser = subparsers.add_parser("email", help="Verify a single email")
    email_parser.add_argument("email", help="Email address to verify")

    # url command
    url_parser = subparsers.add_parser("url", help="Check a single URL")
    url_parser.add_argument("url", help="URL to check")

    # batch command
    batch_parser = subparsers.add_parser("batch", help="Verify contacts from JSON file")
    batch_parser.add_argument("input", help="JSON file with contacts array")
    batch_parser.add_argument("-o", "--output", help="Output JSON path", default="verification_results.json")

    # report command
    report_parser = subparsers.add_parser("report", help="Extract and verify contacts from report")
    report_parser.add_argument("report", help="Path to report markdown file")
    report_parser.add_argument("-o", "--output", help="Output JSON path", default="verification_results.json")

    args = parser.parse_args()

    if args.command == "email":
        cmd_email(args)
    elif args.command == "url":
        cmd_url(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
