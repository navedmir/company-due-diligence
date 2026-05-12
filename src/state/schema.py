from typing import TypedDict, List, Optional, Annotated
from operator import add


class DueDiligenceState(TypedDict):
    # Input
    startup_name: str
    startup_description: str
    funding_stage: Optional[str]

    # Research outputs
    research_outputs: Annotated[List[dict], add]

    # Analysis outputs
    analysis_outputs: Annotated[List[dict], add]

    # Synthesis outputs
    full_report: Optional[str]
    investment_decision: Optional[dict]

    # Metadata
    current_stage: str
    errors: Annotated[List[str], add]
    retry_count: int


def create_initial_state(startup_name: str, startup_description: str, funding_stage: Optional[str] = None) -> DueDiligenceState:
    """Factory function to create the initial state for a due diligence workflow."""
    return DueDiligenceState(
        startup_name=startup_name,
        startup_description=startup_description,
        funding_stage=funding_stage,
        research_outputs=[],
        analysis_outputs=[],
        full_report=None,
        investment_decision=None,
        current_stage="init",
        errors=[],
        retry_count=0,
    )