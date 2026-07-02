"""Reference implementation for Relational AI."""

from .agency import (
    AgencyDimensions,
    AgencyResult,
    AgencyState,
    ConversationSignals,
    DependencyDimensions,
    SelfReport,
    evaluate_agency_trajectory,
)
from .agency_controller import AgencyMaximizer, Layer2AgencyConfig, ResponseMode

__all__ = [
    "AgencyDimensions",
    "AgencyMaximizer",
    "AgencyResult",
    "AgencyState",
    "ConversationSignals",
    "DependencyDimensions",
    "Layer2AgencyConfig",
    "ResponseMode",
    "SelfReport",
    "evaluate_agency_trajectory",
]

