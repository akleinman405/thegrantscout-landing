"""AI package for TheGrantScout Pipeline."""
from .narratives import (
    NarrativeGenerator,
    generate_all_narratives,
    generate_all_fallbacks,
    load_prompt_template
)
from .fallbacks import (
    fallback_why_this_fits,
    fallback_positioning_strategy,
    fallback_next_steps,
    fallback_key_strengths,
    fallback_one_thing
)

__all__ = [
    # Main generator
    'NarrativeGenerator',
    'generate_all_narratives',
    'generate_all_fallbacks',
    'load_prompt_template',

    # Fallbacks
    'fallback_why_this_fits',
    'fallback_positioning_strategy',
    'fallback_next_steps',
    'fallback_key_strengths',
    'fallback_one_thing'
]
