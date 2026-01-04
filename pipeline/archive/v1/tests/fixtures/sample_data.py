"""Sample data fixtures for testing."""

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
    'annual_giving': {
        'total': 2500000,
        'count': 45,
        'year': 2023
    },
    'typical_grant': {
        'median': 45000,
        'min': 5000,
        'max': 150000
    },
    'geographic_focus': {
        'top_state': 'CA',
        'top_state_pct': 0.78,
        'in_state_pct': 0.82
    },
    'repeat_funding': {
        'rate': 0.34,
        'unique_recipients': 120
    },
    'giving_style': {
        'general_support_pct': 0.62
    },
    'recipient_profile': {
        'budget_min': 250000,
        'budget_max': 5000000,
        'primary_sector': 'Education'
    },
    'funding_trend': {
        'direction': 'Growing',
        'change_pct': 0.15
    }
}

SAMPLE_OPPORTUNITY = {
    'rank': 1,
    'foundation_ein': '987654321',
    'foundation_name': 'Sample Foundation',
    'match_score': 85.5,
    'match_probability': 0.855,
    'same_state': True,
    'foundation_state': 'CA',
    'funder_snapshot': SAMPLE_FUNDER_SNAPSHOT,
    'comparable_grant': {
        'recipient_name': 'Oakland Youth Services',
        'amount': 50000,
        'purpose_text': 'Youth education program',
        'tax_year': 2023
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
