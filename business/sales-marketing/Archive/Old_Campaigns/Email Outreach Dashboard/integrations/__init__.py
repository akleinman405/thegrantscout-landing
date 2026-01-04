"""
Integrations package for Campaign Control Center.
Provides interfaces to CSV files, trackers, coordination, and templates.
"""

# CSV Handler
from .csv_handler import (
    read_prospects,
    write_prospects,
    append_prospects,
    deduplicate_prospects,
    validate_prospect_schema,
    get_prospect_count,
    get_prospect_stats,
    export_prospects_to_csv,
    import_prospects_from_csv
)

# Tracker Reader
from .tracker_reader import (
    read_sent_tracker,
    read_response_tracker,
    get_sent_count,
    get_sent_by_date,
    get_sent_by_vertical,
    calculate_response_rate,
    get_daily_metrics,
    get_vertical_breakdown,
    get_account_daily_sent,
    get_metrics,
    clear_cache
)

# Coordination Reader
from .coordination_reader import (
    read_coordination,
    get_allocation_status,
    is_capacity_available,
    get_daily_summary,
    update_coordination,
    reset_daily_coordination,
    pause_campaign,
    resume_campaign,
    get_capacity_allocation,
    get_vertical_status_breakdown
)

# Template Manager
from .template_manager import (
    save_template_to_file,
    read_template_from_file,
    list_template_files,
    delete_template_file,
    sync_templates_to_db,
    sync_templates_from_db,
    export_template_bundle,
    import_template_bundle
)

__all__ = [
    # CSV Handler
    'read_prospects',
    'write_prospects',
    'append_prospects',
    'deduplicate_prospects',
    'validate_prospect_schema',
    'get_prospect_count',
    'get_prospect_stats',
    'export_prospects_to_csv',
    'import_prospects_from_csv',
    # Tracker Reader
    'read_sent_tracker',
    'read_response_tracker',
    'get_sent_count',
    'get_sent_by_date',
    'get_sent_by_vertical',
    'calculate_response_rate',
    'get_daily_metrics',
    'get_vertical_breakdown',
    'get_account_daily_sent',
    'get_metrics',
    'clear_cache',
    # Coordination Reader
    'read_coordination',
    'get_allocation_status',
    'is_capacity_available',
    'get_daily_summary',
    'update_coordination',
    'reset_daily_coordination',
    'pause_campaign',
    'resume_campaign',
    'get_capacity_allocation',
    'get_vertical_status_breakdown',
    # Template Manager
    'save_template_to_file',
    'read_template_from_file',
    'list_template_files',
    'delete_template_file',
    'sync_templates_to_db',
    'sync_templates_from_db',
    'export_template_bundle',
    'import_template_bundle'
]
