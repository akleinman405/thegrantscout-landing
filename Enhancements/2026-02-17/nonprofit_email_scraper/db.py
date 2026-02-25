"""
Database operations for the nonprofit email scraper.

Reads prospects from org_url_enrichment, writes results to web_emails + web_pages,
and updates scrape_status tracking fields.

Uses psycopg2 with f990_2025 schema (same DB as TheGrantScout main project).
"""

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import psycopg2.errors
from psycopg2.extras import RealDictCursor, execute_values

from email_scraper import classify_email_type

SCHEMA = 'f990_2025'


def get_db_config() -> dict:
    """Get database connection config. Reads DATABASE_URL or PG* env vars."""
    # Try loading .env from pipeline directory
    env_path = Path(__file__).resolve().parent.parent.parent.parent / '4. Pipeline' / '.env'
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            pass

    db_url = os.getenv('DATABASE_URL')
    if db_url:
        parsed = urlparse(db_url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/') if parsed.path else 'thegrantscout',
            'user': parsed.username or 'postgres',
            'password': parsed.password or '',
        }

    return {
        'host': os.getenv('PGHOST', 'localhost'),
        'port': int(os.getenv('PGPORT', '5432')),
        'database': os.getenv('PGDATABASE', 'thegrantscout'),
        'user': os.getenv('PGUSER', 'postgres'),
        'password': os.getenv('PGPASSWORD', ''),
    }


class DatabaseManager:
    """Database operations for nonprofit email scraping pipeline."""

    def __init__(self, db_config: dict = None):
        self.db_config = db_config or get_db_config()
        self.conn = psycopg2.connect(**self.db_config)
        self.conn.autocommit = False
        self._set_schema()

    def _set_schema(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('search_path', %s, false)", (SCHEMA,)
            )
        self.conn.commit()

    def _get_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    def get_prospects_to_scrape(self, limit: int = 1000) -> list[dict]:
        """
        Get nonprofit URLs ready for scraping.

        Returns list of dicts with 'ein', 'url', 'org_name', 'state'.
        Only returns orgs that haven't been scraped yet.
        """
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT ein, website_clean AS url, org_name, state
                FROM org_url_enrichment
                WHERE org_type = 'nonprofit'
                  AND url_validated = true
                  AND scrape_status IS NULL
                  AND website_clean IS NOT NULL
                  AND website_clean != ''
                ORDER BY RANDOM()
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]

    def mark_scrape_started(self, eins: list[str]):
        """Mark a batch of EINs as scrape-in-progress to prevent double processing."""
        if not eins:
            return
        with self.conn.cursor() as cur:
            cur.execute(
                """UPDATE org_url_enrichment
                   SET scrape_status = 'in_progress',
                       scrape_started_at = NOW()
                   WHERE ein = ANY(%s) AND scrape_status IS NULL""",
                (eins,),
            )
        self.conn.commit()

    def save_scrape_result(self, result):
        """
        Save a complete ScrapeResult to the database.

        Writes to: web_emails, web_pages, org_url_enrichment (scrape tracking).
        """
        ein = result.ein

        with self.conn.cursor() as cur:
            # 1. Insert emails (ON CONFLICT update if better confidence)
            for email_result in result.emails:
                email_domain = email_result.email.split('@')[1] if '@' in email_result.email else None
                email_type = classify_email_type(email_result.email)
                extraction_method = getattr(email_result, 'extraction_method', 'regex_scrape')
                person_name = getattr(email_result, 'person_name', None)
                person_title = getattr(email_result, 'person_title', None)
                cur.execute("""
                    INSERT INTO web_emails (
                        ein, email, email_type, email_domain, domain_matches_website,
                        source_url, source_page_type, extraction_method,
                        confidence, syntax_valid, person_name, person_title, extracted_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (ein, email) DO UPDATE SET
                        confidence = GREATEST(web_emails.confidence, EXCLUDED.confidence),
                        person_name = COALESCE(EXCLUDED.person_name, web_emails.person_name),
                        person_title = COALESCE(EXCLUDED.person_title, web_emails.person_title),
                        extraction_method = CASE
                            WHEN EXCLUDED.confidence > web_emails.confidence
                            THEN EXCLUDED.extraction_method
                            ELSE web_emails.extraction_method
                        END
                """, (
                    ein,
                    email_result.email,
                    email_type,
                    email_domain,
                    email_result.domain_matches,
                    email_result.source_url,
                    email_result.source_page,
                    extraction_method,
                    email_result.confidence,
                    True,  # regex already validates syntax
                    person_name,
                    person_title,
                ))

            # 2. Insert page fetch logs (ON CONFLICT skip duplicates)
            for page in result.pages:
                cur.execute("""
                    INSERT INTO web_pages (
                        ein, url, page_type, http_status,
                        html_hash, html_size_bytes, fetched_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (ein, url) DO NOTHING
                """, (
                    ein,
                    page.url,
                    page.page_type,
                    page.http_status,
                    page.html_hash,
                    page.html_size,
                ))

            # 3. Update scrape tracking on org_url_enrichment
            pages_fetched = sum(1 for p in result.pages if p.error is None)
            cur.execute("""
                UPDATE org_url_enrichment
                SET scrape_status = %s,
                    scrape_pages_fetched = %s,
                    scrape_completed_at = NOW(),
                    scrape_error = %s
                WHERE ein = %s
            """, (
                result.status,
                pages_fetched,
                result.pages[0].error if result.pages and result.pages[0].error else None,
                ein,
            ))

    def save_batch_results(self, results: list):
        """Save a batch of ScrapeResults. Commits once at the end."""
        for result in results:
            self.save_scrape_result(result)
        self.conn.commit()

    def reset_stuck_in_progress(self, hours: int = 4) -> int:
        """Reset EINs stuck in 'in_progress' for more than N hours back to NULL."""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE org_url_enrichment
                SET scrape_status = NULL,
                    scrape_started_at = NULL
                WHERE scrape_status = 'in_progress'
                  AND scrape_started_at < NOW() - make_interval(hours => %s)
            """, (hours,))
            count = cur.rowcount
        self.conn.commit()
        return count

    def get_unclassified_emails(self) -> list[dict]:
        """Get emails where email_type is NULL."""
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT id, email
                FROM web_emails
                WHERE email_type IS NULL
                ORDER BY id
            """)
            return [dict(row) for row in cur.fetchall()]

    def update_email_types(self, updates: list[tuple[str, int]]):
        """Batch update email_type for a list of (type, id) tuples."""
        if not updates:
            return
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                "UPDATE web_emails SET email_type = data.email_type "
                "FROM (VALUES %s) AS data(email_type, id) "
                "WHERE web_emails.id = data.id",
                updates,
            )
        self.conn.commit()

    def get_cross_org_duplicates(self, min_orgs: int = 3) -> list[dict]:
        """Find emails appearing in min_orgs+ distinct organizations."""
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT email, COUNT(DISTINCT ein) AS org_count, COUNT(*) AS row_count
                FROM web_emails
                GROUP BY email
                HAVING COUNT(DISTINCT ein) >= %s
                ORDER BY org_count DESC
            """, (min_orgs,))
            return [dict(row) for row in cur.fetchall()]

    def delete_cross_org_duplicates(self, min_orgs: int = 3) -> int:
        """Delete emails appearing in min_orgs+ distinct organizations. Returns rows deleted."""
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM web_emails
                WHERE email IN (
                    SELECT email
                    FROM web_emails
                    GROUP BY email
                    HAVING COUNT(DISTINCT ein) >= %s
                )
            """, (min_orgs,))
            deleted = cur.rowcount
        self.conn.commit()
        return deleted

    def get_unvalidated_domains(self) -> list[str]:
        """Get distinct email domains where mx_valid is NULL."""
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT DISTINCT email_domain
                FROM web_emails
                WHERE mx_valid IS NULL AND email_domain IS NOT NULL
                ORDER BY email_domain
            """)
            return [row['email_domain'] for row in cur.fetchall()]

    def update_mx_validation(self, results: list[tuple[bool, str]]):
        """Batch update mx_valid and validated_at for domains.
        Args:
            results: list of (mx_valid_bool, domain) tuples.
        """
        if not results:
            return
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                "UPDATE web_emails SET mx_valid = data.mx_valid, validated_at = NOW() "
                "FROM (VALUES %s) AS data(mx_valid, domain) "
                "WHERE web_emails.email_domain = data.domain AND web_emails.mx_valid IS NULL",
                results,
            )
        self.conn.commit()

    def fix_existing_emails(self, dry_run: bool = True) -> dict:
        """Fix existing emails: delete junk, strip @www., reclassify types.
        Returns dict with counts of each fix applied."""
        import re as _re

        # Junk patterns to match (same as JUNK_PATTERNS + EXCLUDE_PATTERNS additions)
        new_junk_patterns = [
            r'@company\.com$', r'@yoursite\.com$', r'@yourdomain\.', r'@domain\.com$',
            r'@site\.com$', r'@emailserver\.com$', r'@contoh\.com$', r'@ejemplo\.com$',
            r'@company-domain\.com$', r'@mysite\.com$',
            r'@enfold-restaurant\.com', r'@events\.frontend',
            r'@[^@]+\.(frontend|tld)$',
            r'^email@', r'^yourname@', r'^youremail@', r'^address@domain\.',
            r'^first\.last@company\.com$', r'^you@yourdomain', r'^you@email',
            r'^ejemplo@',
            r'\.azurewebsites\.net$', r'\.netlify\.app$', r'\.herokuapp\.com$',
            r'\.vercel\.app$',
        ]
        compiled = [_re.compile(p, _re.IGNORECASE) for p in new_junk_patterns]

        counts = {'junk_deleted': 0, 'www_fixed': 0, 'types_reclassified': 0}

        with self._get_cursor() as cur:
            # 1. Find and delete junk emails
            cur.execute("SELECT id, email FROM web_emails")
            junk_ids = []
            for row in cur.fetchall():
                for pattern in compiled:
                    if pattern.search(row['email']):
                        junk_ids.append(row['id'])
                        break

            counts['junk_deleted'] = len(junk_ids)

            # 2. Find @www. emails
            cur.execute("SELECT id, email, ein FROM web_emails WHERE email LIKE '%@www.%'")
            www_rows = cur.fetchall()
            counts['www_fixed'] = len(www_rows)

            # 3. Count emails needing reclassification
            cur.execute("SELECT COUNT(*) AS cnt FROM web_emails WHERE email_type IS NULL")
            counts['types_reclassified'] = cur.fetchone()['cnt']

        if not dry_run:
            with self.conn.cursor() as cur:
                # Delete junk
                if junk_ids:
                    cur.execute("DELETE FROM web_emails WHERE id = ANY(%s)", (junk_ids,))

                # Fix @www. emails (use savepoints to handle unique constraint violations)
                for row in www_rows:
                    fixed = row['email'].replace('@www.', '@')
                    fixed_domain = fixed.split('@')[1] if '@' in fixed else None
                    cur.execute("SAVEPOINT www_fix")
                    try:
                        cur.execute(
                            "UPDATE web_emails SET email = %s, email_domain = %s WHERE id = %s",
                            (fixed, fixed_domain, row['id']),
                        )
                        cur.execute("RELEASE SAVEPOINT www_fix")
                    except psycopg2.IntegrityError:
                        # Unique constraint violation: fixed email already exists — delete the www. version
                        cur.execute("ROLLBACK TO SAVEPOINT www_fix")
                        cur.execute("DELETE FROM web_emails WHERE id = %s", (row['id'],))

                # Reclassify email types — batch with execute_values
                cur.execute("SELECT id, email FROM web_emails WHERE email_type IS NULL")
                unclassified = cur.fetchall()
                if unclassified:
                    updates = [
                        (classify_email_type(row[1]), row[0])
                        for row in unclassified
                    ]
                    execute_values(
                        cur,
                        "UPDATE web_emails SET email_type = data.email_type "
                        "FROM (VALUES %s) AS data(email_type, id) "
                        "WHERE web_emails.id = data.id",
                        updates,
                    )

            self.conn.commit()

        return counts

    def reset_not_found_for_rescrape(self, dry_run: bool = True) -> int:
        """Reset scrape_status for 'not_found' rows so they get rescraped.
        Returns count of rows that would be / were reset."""
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt
                FROM org_url_enrichment
                WHERE scrape_status = 'not_found'
                  AND org_type = 'nonprofit'
                  AND url_validated = true
            """)
            count = cur.fetchone()['cnt']

        if not dry_run:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE org_url_enrichment
                    SET scrape_status = NULL,
                        scrape_started_at = NULL,
                        scrape_completed_at = NULL,
                        scrape_pages_fetched = NULL,
                        scrape_error = NULL
                    WHERE scrape_status = 'not_found'
                      AND org_type = 'nonprofit'
                      AND url_validated = true
                """)
            self.conn.commit()

        return count

    def get_stats(self) -> dict:
        """Get pipeline progress statistics."""
        with self._get_cursor() as cur:
            # Total nonprofits with validated URLs
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM org_url_enrichment
                WHERE org_type = 'nonprofit' AND url_validated = true
            """)
            total = cur.fetchone()['total']

            # Scrape status breakdown
            cur.execute("""
                SELECT
                    COALESCE(scrape_status, 'pending') AS status,
                    COUNT(*) AS cnt
                FROM org_url_enrichment
                WHERE org_type = 'nonprofit' AND url_validated = true
                GROUP BY scrape_status
                ORDER BY cnt DESC
            """)
            status_breakdown = {row['status']: row['cnt'] for row in cur.fetchall()}

            # Emails found
            cur.execute("SELECT COUNT(*) AS cnt FROM web_emails")
            emails_found = cur.fetchone()['cnt']

            # Distinct EINs with emails
            cur.execute("SELECT COUNT(DISTINCT ein) AS cnt FROM web_emails")
            eins_with_email = cur.fetchone()['cnt']

            # Pages fetched
            cur.execute("SELECT COUNT(*) AS cnt FROM web_pages")
            pages_fetched = cur.fetchone()['cnt']

            # Average emails per org (among those with emails)
            cur.execute("""
                SELECT ROUND(AVG(email_count), 1) AS avg_emails
                FROM (
                    SELECT ein, COUNT(*) AS email_count
                    FROM web_emails
                    GROUP BY ein
                ) sub
            """)
            row = cur.fetchone()
            avg_emails = row['avg_emails'] if row and row['avg_emails'] else 0

            # Confidence distribution
            cur.execute("""
                SELECT
                    CASE
                        WHEN confidence >= 0.8 THEN 'high (0.8+)'
                        WHEN confidence >= 0.5 THEN 'medium (0.5-0.8)'
                        ELSE 'low (<0.5)'
                    END AS tier,
                    COUNT(*) AS cnt
                FROM web_emails
                GROUP BY tier
                ORDER BY tier
            """)
            confidence_dist = {row['tier']: row['cnt'] for row in cur.fetchall()}

            # Email type distribution
            cur.execute("""
                SELECT COALESCE(email_type, 'unclassified') AS etype, COUNT(*) AS cnt
                FROM web_emails
                GROUP BY email_type
                ORDER BY cnt DESC
            """)
            email_type_dist = {row['etype']: row['cnt'] for row in cur.fetchall()}

            # MX validation
            cur.execute("""
                SELECT
                    CASE
                        WHEN mx_valid IS NULL THEN 'not checked'
                        WHEN mx_valid = true THEN 'valid'
                        ELSE 'invalid'
                    END AS mx_status,
                    COUNT(*) AS cnt
                FROM web_emails
                GROUP BY mx_status
                ORDER BY cnt DESC
            """)
            mx_validation = {row['mx_status']: row['cnt'] for row in cur.fetchall()}

        return {
            'total_prospects': total,
            'status_breakdown': status_breakdown,
            'emails_found': emails_found,
            'eins_with_email': eins_with_email,
            'pages_fetched': pages_fetched,
            'avg_emails_per_org': avg_emails,
            'confidence_distribution': confidence_dist,
            'email_type_distribution': email_type_dist,
            'mx_validation': mx_validation,
        }
