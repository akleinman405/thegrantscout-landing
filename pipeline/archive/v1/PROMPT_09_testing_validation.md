# PROMPT_09: Phase 9 - Testing & Validation

**Date:** 2025-12-27
**Phase:** 9
**Agent:** Dev Team + Research Team
**Estimated Time:** 5-6 hours
**Depends On:** PROMPT_08 (Pipeline) complete

---

## Objective

Create comprehensive tests, validate the pipeline on beta clients, and ensure production readiness.

---

## Context

The pipeline is now complete. This phase:
1. Creates unit tests for each module
2. Creates integration tests for the full pipeline
3. Validates output quality on real clients
4. Documents any issues and fixes

---

## Tasks

### Task 1: Create Test Fixtures

Create sample data for testing.

```python
# tests/fixtures/sample_data.py

SAMPLE_CLIENT = {
    'organization_name': 'Test Nonprofit',
    'ein': '123456789',
    'email': 'test@example.org',
    'state': 'CA',
    'city': 'Oakland',
    'budget': '$500,000 - $1 million',
    'budget_numeric': 750000,
    'grant_size_target': '$25,000 - $100,000',
    'org_type': '501(c)(3)',
    'program_areas': ['Education', 'Youth Development'],
    'populations_served': ['Low-income youth', 'Students'],
    'geographic_scope': 'Local/City',
    'ntee_code': 'B20',
    'mission_statement': 'We provide after-school tutoring and mentorship to low-income youth in Oakland.',
    'prior_funders': ['Local Community Foundation'],
    'notes': None
}

SAMPLE_FUNDER_SNAPSHOT = {
    'foundation_ein': '987654321',
    'foundation_name': 'Sample Foundation',
    'annual_giving_total': 2500000,
    'annual_giving_count': 45,
    'annual_giving_year': 2023,
    'typical_grant_median': 45000,
    'typical_grant_min': 5000,
    'typical_grant_max': 150000,
    'geographic_top_state': 'CA',
    'geographic_top_state_pct': 0.78,
    'geographic_in_state_pct': 0.82,
    'repeat_funding_rate': 0.34,
    'unique_recipients': 120,
    'giving_style_general_pct': 0.62,
    'giving_style_program_pct': 0.38,
    'recipient_budget_min': 250000,
    'recipient_budget_max': 5000000,
    'recipient_primary_sector': 'Education',
    'funding_trend_direction': 'Growing',
    'funding_trend_change_pct': 0.15
}

SAMPLE_OPPORTUNITY = {
    'rank': 1,
    'foundation_ein': '987654321',
    'foundation_name': 'Sample Foundation',
    'match_score': 85.5,
    'match_probability': 0.855,
    'funder_snapshot': SAMPLE_FUNDER_SNAPSHOT,
    'comparable_grant': {
        'recipient_name': 'Oakland Youth Services',
        'grant_amount': 50000,
        'grant_purpose': 'Youth education program',
        'grant_year': 2023
    },
    'potential_connections': [],
    'amount_min': 25000,
    'amount_max': 75000,
    'deadline': 'Rolling',
    'portal_url': 'https://example.org/apply',
    'contact_name': 'Jane Smith',
    'contact_email': 'jsmith@example.org',
    'contact_phone': '555-123-4567',
    'application_requirements': ['LOI', '501c3 letter', 'Budget'],
    'why_this_fits': None,
    'positioning_strategy': None,
    'next_steps': [],
    'status': 'HIGH',
    'effort': 'Medium',
    'fit_score': 9
}
```

### Task 2: Create Unit Tests - Scoring

```python
# tests/test_scoring.py

import pytest
from scoring.scoring import GrantScorer
from scoring.features import calculate_features, get_foundation_features


class TestFeatures:
    """Test feature calculation."""
    
    def test_get_foundation_features_returns_dict(self):
        """Foundation features returns dictionary."""
        features = get_foundation_features('SAMPLE_EIN')
        assert isinstance(features, dict)
    
    def test_calculate_features_all_present(self):
        """All expected features are calculated."""
        features = calculate_features('FOUNDATION_EIN', 'RECIPIENT_EIN')
        
        # Check key features exist
        assert 'match_same_state' in features
        assert 'f_total_grants' in features
        
    def test_calculate_features_handles_missing(self):
        """Missing data handled gracefully."""
        # Use a nonexistent EIN
        features = calculate_features('000000000', '000000001')
        # Should return dict with None/default values, not crash
        assert isinstance(features, dict)


class TestScorer:
    """Test scoring functionality."""
    
    @pytest.fixture
    def scorer(self):
        return GrantScorer()
    
    def test_score_pair_returns_float(self, scorer):
        """Single pair scoring returns probability."""
        score = scorer.score_pair('FOUNDATION_EIN', 'RECIPIENT_EIN')
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_score_nonprofit_returns_dataframe(self, scorer):
        """Nonprofit scoring returns ranked DataFrame."""
        results = scorer.score_nonprofit('RECIPIENT_EIN', top_k=10)
        
        assert len(results) == 10
        assert 'match_score' in results.columns
        assert 'match_rank' in results.columns
        assert 'foundation_ein' in results.columns
    
    def test_scores_are_sorted(self, scorer):
        """Results are sorted by score descending."""
        results = scorer.score_nonprofit('RECIPIENT_EIN', top_k=10)
        
        scores = results['match_score'].tolist()
        assert scores == sorted(scores, reverse=True)
    
    def test_exclude_prior_funders(self, scorer):
        """Prior funders can be excluded."""
        with_exclusion = scorer.score_nonprofit('RECIPIENT_EIN', exclude_prior_funders=True)
        without_exclusion = scorer.score_nonprofit('RECIPIENT_EIN', exclude_prior_funders=False)
        
        # Without exclusion should have >= results (may include prior funders)
        assert len(without_exclusion) >= len(with_exclusion)
```

### Task 3: Create Unit Tests - Enrichment

```python
# tests/test_enrichment.py

import pytest
from enrichment import get_funder_snapshot, find_comparable_grant, find_connections
from enrichment.cache import SnapshotCache


class TestFunderSnapshot:
    """Test funder snapshot retrieval."""
    
    def test_get_snapshot_returns_object(self):
        """Snapshot returns FunderSnapshot object."""
        snapshot = get_funder_snapshot('SAMPLE_EIN')
        
        assert snapshot is not None
        assert hasattr(snapshot, 'annual_giving_total')
        assert hasattr(snapshot, 'typical_grant_median')
    
    def test_snapshot_has_all_metrics(self):
        """Snapshot contains all 8 required metrics."""
        snapshot = get_funder_snapshot('SAMPLE_EIN')
        
        required_fields = [
            'annual_giving_total',
            'typical_grant_median',
            'geographic_top_state',
            'repeat_funding_rate',
            'giving_style_general_pct',
            'recipient_primary_sector',
            'funding_trend_direction'
        ]
        
        for field in required_fields:
            assert hasattr(snapshot, field), f"Missing field: {field}"
    
    def test_snapshot_to_dict(self):
        """Snapshot can be converted to dict."""
        snapshot = get_funder_snapshot('SAMPLE_EIN')
        d = snapshot.to_dict()
        
        assert isinstance(d, dict)
        assert 'foundation_ein' in d


class TestCache:
    """Test caching functionality."""
    
    @pytest.fixture
    def cache(self, tmp_path):
        return SnapshotCache(cache_dir=str(tmp_path), ttl_days=1)
    
    def test_cache_miss_returns_none(self, cache):
        """Cache miss returns None."""
        result = cache.get('nonexistent_ein')
        assert result is None
    
    def test_cache_stores_and_retrieves(self, cache):
        """Cache stores and retrieves data."""
        snapshot = get_funder_snapshot('SAMPLE_EIN')
        cache.set('SAMPLE_EIN', snapshot)
        
        retrieved = cache.get('SAMPLE_EIN')
        assert retrieved is not None
        assert retrieved.foundation_ein == snapshot.foundation_ein


class TestComparableGrant:
    """Test comparable grant finding."""
    
    def test_find_comparable_grant(self):
        """Finds a comparable grant."""
        grant = find_comparable_grant(
            foundation_ein='SAMPLE_EIN',
            client_state='CA',
            client_ntee='B20'
        )
        
        # May return None if no match, but shouldn't crash
        if grant:
            assert hasattr(grant, 'recipient_name')
            assert hasattr(grant, 'grant_amount')
```

### Task 4: Create Unit Tests - AI Narratives

```python
# tests/test_narratives.py

import pytest
from ai.narratives import NarrativeGenerator, generate_all_narratives
from ai.fallbacks import fallback_why_this_fits, fallback_positioning_strategy
from tests.fixtures.sample_data import SAMPLE_CLIENT, SAMPLE_OPPORTUNITY


class TestFallbacks:
    """Test fallback narrative generation."""
    
    def test_fallback_why_this_fits(self):
        """Fallback generates text."""
        text = fallback_why_this_fits(SAMPLE_CLIENT, SAMPLE_OPPORTUNITY)
        
        assert isinstance(text, str)
        assert len(text) > 50
        assert SAMPLE_OPPORTUNITY['foundation_name'] in text
    
    def test_fallback_positioning(self):
        """Fallback generates positioning text."""
        text = fallback_positioning_strategy(SAMPLE_CLIENT, SAMPLE_OPPORTUNITY)
        
        assert isinstance(text, str)
        assert len(text) > 50


class TestNarrativeGeneration:
    """Test AI narrative generation (requires API key)."""
    
    @pytest.fixture
    def generator(self):
        return NarrativeGenerator()
    
    @pytest.mark.skipif(
        not os.getenv('ANTHROPIC_API_KEY'),
        reason="API key not available"
    )
    def test_generate_why_this_fits(self, generator):
        """AI generates Why This Fits."""
        text = generator.generate_why_this_fits(SAMPLE_CLIENT, SAMPLE_OPPORTUNITY)
        
        assert isinstance(text, str)
        assert len(text) > 100
        # Should reference specific data
        assert any(term in text.lower() for term in ['oakland', 'california', 'education'])
    
    def test_generate_all_with_fallbacks(self):
        """Generate all narratives using fallbacks."""
        result = generate_all_narratives(
            client=SAMPLE_CLIENT,
            opportunities=[SAMPLE_OPPORTUNITY],
            use_fallbacks=True
        )
        
        assert 'opportunities' in result
        assert 'executive_summary' in result
        assert result['opportunities'][0]['why_this_fits'] is not None
```

### Task 5: Create Integration Tests

```python
# tests/test_pipeline.py

import pytest
from pathlib import Path
from generate_report import generate_report
from assembly.report_data import assemble_report_data
from rendering import ReportRenderer


class TestAssembly:
    """Test report data assembly."""
    
    def test_assemble_report_data(self):
        """Assembly creates complete report data."""
        report = assemble_report_data(
            client_identifier="Test Client",
            top_k=5
        )
        
        assert report is not None
        assert hasattr(report, 'client')
        assert hasattr(report, 'opportunities')
        assert len(report.opportunities) == 5
    
    def test_report_data_to_json(self, tmp_path):
        """Report data exports to valid JSON."""
        report = assemble_report_data("Test Client")
        
        json_path = tmp_path / "test_report.json"
        report.to_json(str(json_path))
        
        assert json_path.exists()


class TestRendering:
    """Test markdown rendering."""
    
    @pytest.fixture
    def renderer(self):
        return ReportRenderer()
    
    def test_render_returns_markdown(self, renderer):
        """Renderer produces markdown string."""
        report = assemble_report_data("Test Client")
        md = renderer.render(report.to_dict())
        
        assert isinstance(md, str)
        assert len(md) > 1000
    
    def test_render_has_required_sections(self, renderer):
        """Rendered markdown has all sections."""
        report = assemble_report_data("Test Client")
        md = renderer.render(report.to_dict())
        
        required_sections = [
            "# ",  # Header
            "## If You Only Do One Thing",
            "## Executive Summary",
            "## This Week's Top 5",
            "## Opportunity #1",
            "## 8-Week Timeline",
            "## Quick Reference"
        ]
        
        for section in required_sections:
            assert section in md, f"Missing section: {section}"
    
    def test_render_no_unfilled_placeholders(self, renderer):
        """No placeholder variables in output."""
        report = assemble_report_data("Test Client")
        md = renderer.render(report.to_dict())
        
        # Check for unfilled {placeholders}
        import re
        placeholders = re.findall(r'\{[a-z_]+\}', md)
        assert len(placeholders) == 0, f"Unfilled placeholders: {placeholders}"


class TestFullPipeline:
    """Test end-to-end pipeline."""
    
    def test_dry_run_generates_files(self, tmp_path):
        """Dry run generates markdown file."""
        output_path = generate_report(
            client_identifier="Test Client",
            output_dir=str(tmp_path),
            dry_run=True
        )
        
        assert Path(output_path).exists()
    
    def test_pipeline_timing(self, tmp_path):
        """Pipeline completes in reasonable time."""
        import time
        
        start = time.time()
        generate_report(
            client_identifier="Test Client",
            output_dir=str(tmp_path),
            dry_run=True
        )
        elapsed = time.time() - start
        
        assert elapsed < 60, f"Pipeline too slow: {elapsed:.1f}s"
```

### Task 6: Create Quality Checklist

```python
# tests/quality_checklist.py

"""
Quality checklist for generated reports.
Run manually on generated reports.
"""

from pathlib import Path
import re


def check_report_quality(md_path: str) -> dict:
    """
    Run quality checks on a generated report.
    
    Returns dict with check results.
    """
    with open(md_path) as f:
        content = f.read()
    
    results = {}
    
    # 1. Has all required sections
    required_sections = [
        ("Header", r"^# .+\n# Week \d+ Grant"),
        ("One Thing", r"## If You Only Do One Thing"),
        ("Executive Summary", r"## Executive Summary"),
        ("Top 5 Table", r"## This Week's Top 5"),
        ("Opportunity 1", r"## Opportunity #1"),
        ("Opportunity 5", r"## Opportunity #5"),
        ("Timeline", r"## 8-Week Timeline"),
        ("Quick Reference", r"## Quick Reference")
    ]
    
    for name, pattern in required_sections:
        results[f"section_{name}"] = bool(re.search(pattern, content))
    
    # 2. No unfilled placeholders
    placeholders = re.findall(r'\{[a-z_]+\}', content)
    results["no_placeholders"] = len(placeholders) == 0
    results["placeholder_count"] = len(placeholders)
    
    # 3. Tables are formatted
    results["tables_formatted"] = "|---|" in content
    
    # 4. Dollar amounts formatted
    dollar_amounts = re.findall(r'\$[\d,]+', content)
    results["has_dollar_amounts"] = len(dollar_amounts) > 0
    
    # 5. Dates present
    dates = re.findall(r'\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4}', content)
    results["has_dates"] = len(dates) > 0
    
    # 6. Length check
    results["content_length"] = len(content)
    results["reasonable_length"] = 5000 < len(content) < 50000
    
    # 7. No error messages
    error_patterns = ["Error:", "Failed:", "None", "null", "undefined"]
    results["no_errors"] = not any(p in content for p in error_patterns)
    
    return results


def print_quality_report(results: dict):
    """Print formatted quality report."""
    print("\n" + "="*50)
    print("QUALITY CHECK RESULTS")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for check, result in results.items():
        if isinstance(result, bool):
            status = "✓" if result else "✗"
            if result:
                passed += 1
            else:
                failed += 1
            print(f"{status} {check}: {result}")
        else:
            print(f"  {check}: {result}")
    
    print("="*50)
    print(f"Passed: {passed}, Failed: {failed}")
    print("="*50 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python quality_checklist.py <report.md>")
        sys.exit(1)
    
    results = check_report_quality(sys.argv[1])
    print_quality_report(results)
```

### Task 7: Validate on Beta Clients

Run the pipeline on actual beta clients and validate output quality.

**Beta Clients:**
1. PSMF (Patient Safety Movement Foundation)
2. SNS (Senior Network Services)
3. RHF (Retirement Housing Foundation)

**For each client:**
1. Run full pipeline (not dry-run)
2. Run quality checklist
3. Manual review of output
4. Document any issues

```bash
# Generate reports
python generate_report.py --client "Patient Safety Movement Foundation" -v
python generate_report.py --client "Senior Network Services" -v
python generate_report.py --client "Retirement Housing Foundation" -v

# Run quality checks
python tests/quality_checklist.py outputs/reports/PSMF_*.md
python tests/quality_checklist.py outputs/reports/SNS_*.md
python tests/quality_checklist.py outputs/reports/RHF_*.md
```

---

## Output Files

| File | Description |
|------|-------------|
| `tests/__init__.py` | Package init |
| `tests/fixtures/sample_data.py` | Test data fixtures |
| `tests/test_scoring.py` | Scoring unit tests |
| `tests/test_enrichment.py` | Enrichment unit tests |
| `tests/test_narratives.py` | AI narrative tests |
| `tests/test_pipeline.py` | Integration tests |
| `tests/quality_checklist.py` | Manual quality checker |

---

## Done Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Quality checklist passes for 3 beta clients
- [ ] Reports generated in < 5 minutes each
- [ ] No critical errors in logs
- [ ] Word documents open correctly
- [ ] Manual review shows acceptable quality

---

## Verification Tests

### Run All Tests
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Expected Coverage
- scoring/: >80%
- enrichment/: >80%
- ai/: >70%
- rendering/: >80%
- Overall: >75%

---

## Quality Review Criteria

For each generated report, verify:

| Check | Criteria |
|-------|----------|
| **Scoring** | Top 5 foundations are reasonable matches (not random) |
| **Data** | Funder snapshots have all 8 metrics |
| **AI - Specificity** | Narratives reference specific data (not generic) |
| **AI - Length** | Narratives are 3-4 sentences (not too long/short) |
| **Formatting** | Tables render correctly |
| **Formatting** | Dollar amounts have commas |
| **Accuracy** | Grant amounts are realistic |
| **Completeness** | All 5 opportunities have all sections |
| **Word Doc** | Opens correctly, branding applied |

---

## Handoff

After completion:
1. All tests pass
2. 3 beta client reports validated
3. Quality issues documented
4. Pipeline ready for production use

---

## Final Deliverable

A production-ready pipeline that:
1. Takes a client name or EIN
2. Generates a professional grant report
3. Outputs both .md and .docx files
4. Completes in < 5 minutes
5. Has >75% test coverage
6. Handles errors gracefully

---

*This completes the pipeline build. The system is ready for production use.*
