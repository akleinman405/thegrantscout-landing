"""
Reusable UI components for Campaign Control Center dashboard.
"""

from .cards import metric_card, status_card, info_card, account_card, vertical_card
from .charts import (
    line_chart_emails_over_time,
    bar_chart_by_vertical,
    donut_chart_response_rates,
    progress_bar_quota,
    stacked_bar_chart_campaign_status,
    gauge_chart_capacity
)
from .forms import (
    email_account_form,
    vertical_form,
    template_editor_form,
    settings_form
)
from .tables import (
    prospects_table,
    accounts_table,
    verticals_table,
    templates_table,
    campaign_status_table,
    assignment_matrix
)

__all__ = [
    'metric_card',
    'status_card',
    'info_card',
    'account_card',
    'vertical_card',
    'line_chart_emails_over_time',
    'bar_chart_by_vertical',
    'donut_chart_response_rates',
    'progress_bar_quota',
    'stacked_bar_chart_campaign_status',
    'gauge_chart_capacity',
    'email_account_form',
    'vertical_form',
    'template_editor_form',
    'settings_form',
    'prospects_table',
    'accounts_table',
    'verticals_table',
    'templates_table',
    'campaign_status_table',
    'assignment_matrix',
]
