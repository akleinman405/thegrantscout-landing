"""Assembly package for TheGrantScout Pipeline."""
from .report_data import (
    ReportData,
    Opportunity,
    assemble_report_data,
    calculate_effort,
    calculate_fit_score
)

__all__ = [
    'ReportData',
    'Opportunity',
    'assemble_report_data',
    'calculate_effort',
    'calculate_fit_score'
]
