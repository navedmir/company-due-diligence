from typing import Literal
from ..state.schema import DueDiligenceState

def check_init_success(state: DueDiligenceState) -> Literal["success", "failed"]:
    """Check if the init node completed successfully."""
    errors = state.get("errors", [])
    critical_errors = [e for e in errors if "required" in e.lower()]
    if critical_errors:
        return "failed"
    
    return "success"

def check_research_completeness(state: DueDiligenceState) -> Literal["complete", "incomplete", "failed"]:
    """Check if the research node completed successfully."""
    research_outputs = state.get("research_outputs", [])
    retry_count = state.get("retry_count", 0)

    if not research_outputs:
        if retry_count < 2:
            return "incomplete"
        else:
            return "failed"

    
    total_count = len(research_outputs)

    if total_count == 0:
        return "failed"

    success_count = sum(
        1 for r in research_outputs
        if r.get("success", False)
    )

    success_rate = success_count / total_count

    # Need at least 50% success to continue
    if success_rate >= 0.5:
        return "complete"

    # Can retry up to 2 times
    if retry_count < 2:
        return "incomplete"

    # Too many retries, proceed with what we have
    return "complete"
