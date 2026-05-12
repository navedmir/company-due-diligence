import asyncio
from typing import Any, Dict
from ..state.schema import DueDiligenceState
from ..agents.research import (
    run_company_profiler,
    run_market_researcher,
    run_competitor_scout,
    run_team_investigator,
    run_news_monitor,
)
from ..agents.analysis import (
    run_financial_analyst,
    run_risk_assessor,
    run_tech_evaluator,
    run_legal_reviewer,
)
from ..agents.synthesis import run_report_generator, run_decision_agent


async def init_node(state: DueDiligenceState) -> Dict[str, Any]:
    """Initial node of the workflow."""
    print("Running: init_node")
    print(f" Startup Name: {state.get('startup_name')}")
    return {"current_stage": "init_complete"}

async def research_node(state: dict) -> Dict[str, Any]:
    """Node for conducting research on the startup."""
    # Placeholder for research logic
    print("Running: research_node")

    startup_name = state.get('startup_name')
    startup_description = state.get('startup_description')

    agent_names = [
        "company_profiler",
        "market_researcher",
        "competitor_scout",
        "team_investigator",
        "news_monitor"
    ]

    tasks = [
        run_company_profiler(startup_name, startup_description),
        run_market_researcher(startup_name, startup_description),
        run_competitor_scout(startup_name, startup_description),
        run_team_investigator(startup_name),
        run_news_monitor(startup_name),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    research_outputs = []
    errors = []

    for i, result in enumerate(results):
        agent_name = agent_names[i]
        if isinstance(result, Exception):
            # Handle exception
            errors.append(f"{agent_name}: {str(result)}")
            research_outputs.append({
                "agent": agent_name,
                "output": None,
                "success": False,
                "error": str(result)
            })
            print(f"  FAILED: {agent_name} - {str(result)[:50]}")
        elif not result.success:
            # Handle agent failure
            errors.append(f"{agent_name}: {result.error}")
            research_outputs.append({
                "agent": agent_name,
                "output": None,
                "success": False,
                "error": result.error
            })
            print(f"  FAILED: {agent_name} - {result.error[:50] if result.error else 'Unknown'}")
        else:
            # Success - use result.output
            research_outputs.append({
                "agent": agent_name,
                "output": result.output,
                "raw_output": result.raw_output,
                "success": True,
                "execution_time_ms": result.execution_time_ms
            })
            print(f"  DONE: {agent_name} ({result.execution_time_ms/1000:.1f}s)")

    
    success_count = sum(1 for r in research_outputs if r.get("success"))
    print(f"\nResearch complete: {success_count}/5 agents")
    
    return {
        "research_outputs": research_outputs,
        "errors": errors,
        "current_stage": "research_complete"
    }

async def validate_research_node(state: dict) -> Dict[str, Any]:
    """Node for validating research outputs."""
    print("Running: validate_research_node")
    research_outputs = state.get("research_outputs", [])
    success_count = sum(1 for r in research_outputs if r.get("success", False))
    total_count = len(research_outputs)

    errors = []

    if total_count > 0 and success_count/total_count < 0.5:
        errors.append(f"CRITICAL: Only {success_count}/{total_count} research agents succeeded")
        print(f"CRITICAL: Only {success_count}/{total_count} succeeded")
    else:
        print(f"Validation passed: {success_count}/{total_count} succeeded")

    
    return {
        "current_stage": "research_validated",
        "errors": errors
    }

def _get_agent_output(outputs: List[Dict], agent_name: str) -> Any:
    """Helper function to extract output for a specific agent."""
    for output in outputs:
        if output.get("agent") == agent_name and output.get("success"):
            return output.get("output")
    return None


async def analysis_node(state: dict) -> Dict[str, Any]:
    """Node for analyzing the research outputs."""
    # Placeholder for analysis logic
    print("Running: analysis_node")
    startup_name = state.get('startup_name')
    startup_description = state.get('startup_description')
    research_outputs = state.get("research_outputs", [])

    company_profiler = _get_agent_output(research_outputs, "company_profiler")
    market_researcher = _get_agent_output(research_outputs,"market_researcher")
    team_investigator = _get_agent_output(research_outputs, "team_investigator")


    tasks = [
        run_financial_analyst(startup_name, startup_description, company_profiler, market_researcher),
        run_tech_evaluator(startup_name, startup_description, team_investigator),
        run_legal_reviewer(startup_name, market_researcher)
    ]

    first_batch_results = await asyncio.gather(*tasks, return_exceptions=True)

    analysis_outputs = []
    errors = []

    first_batch_names = ["financial_analyst", "tech_evaluator", "legal_reviewer"]
    for i, result in enumerate(first_batch_results):
        agent_name = first_batch_names[i]
        if isinstance(result, Exception):
            errors.append(f"{agent_name}: {str(result)}")
            analysis_outputs.append({
                "agent": agent_name, "output": None,
                "success": False, "error": str(result)
            })
            print(f"  FAILED: {agent_name}")
        elif not result.success:
            errors.append(f"{agent_name}: {result.error}")
            analysis_outputs.append({
                "agent": agent_name, "output": None,
                "success": False, "error": result.error
            })
            print(f"  FAILED: {agent_name}")
        else:
            analysis_outputs.append({
                "agent": agent_name,
                "output": result.output,
                "raw_output": result.raw_output,
                "success": True,
                "execution_time_ms": result.execution_time_ms
            })
            print(f"  DONE: {agent_name} ({result.execution_time_ms/1000:.1f}s)")

    print("  Starting: risk_assessor (needs other analysis)")
    risk_result = await run_risk_assessor(
        research_outputs=research_outputs,
        analysis_outputs=analysis_outputs,
        startup_name=startup_name
    )

    if isinstance(risk_result, Exception) or not risk_result.success:
        error_msg = str(risk_result) if isinstance(risk_result, Exception) else risk_result.error
        errors.append(f"risk_assessor: {error_msg}")
        analysis_outputs.append({
            "agent": "risk_assessor", "output": None,
            "success": False, "error": error_msg
        })
        print(f"  FAILED: risk_assessor")
    else:
        analysis_outputs.append({
            "agent": "risk_assessor",
            "output": risk_result.output,
            "raw_output": risk_result.raw_output,
            "success": True,
            "execution_time_ms": risk_result.execution_time_ms
        })
        print(f"  DONE: risk_assessor ({risk_result.execution_time_ms/1000:.1f}s)")

    success_count = sum(1 for r in analysis_outputs if r.get("success"))
    print(f"\nAnalysis complete: {success_count}/4 agents")

    return {
        "analysis_outputs": analysis_outputs,
        "errors": errors,
        "current_stage": "analysis_complete"
    }

async def synthesis_node(state: dict) -> Dict[str, Any]:
    """Node for synthesizing the analysis into a final report."""
   
    print("Running: synthesis_node")
    startup_name = state.get('startup_name')
    startup_description = state.get('startup_description')
    research_outputs = state.get("research_outputs", [])
    analysis_outputs = state.get("analysis_outputs", [])
    errors = []

    report_result = await run_report_generator(startup_name, startup_description, research_outputs, analysis_outputs)

    full_report = None
    if isinstance(report_result, Exception) or not report_result.success:
        error_msg = str(report_result) if isinstance(report_result, Exception) else report_result.error
        errors.append(f"report_generator: {error_msg}")
        print(f"  FAILED: report_generator")
    else:
        full_report = report_result.output or report_result.raw_output
        print(f"  DONE: report_generator ({report_result.execution_time_ms/1000:.1f}s)")
    
    print("  Starting: decision_agent")
    risk_assessment = _get_agent_output(analysis_outputs, "risk_assessor")
    decision_result = await run_decision_agent(startup_name,full_report[:4000] if full_report else "", risk_assessment, research_outputs, analysis_outputs)

    investment_decision = None
    if isinstance(decision_result, Exception) or not decision_result.success:
        error_msg = str(decision_result) if isinstance(decision_result, Exception) else decision_result.error
        errors.append(f"decision_agent: {error_msg}")
        print(f"  FAILED: decision_agent")
    else:
        investment_decision = decision_result.output
        print(f"  DONE: decision_agent ({decision_result.execution_time_ms/1000:.1f}s)")

    success_count = (1 if full_report else 0) + (1 if investment_decision else 0)
    print(f"\nSynthesis complete: {success_count}/2 agents")

    return {
        "full_report": full_report,
        "investment_decision": investment_decision,
        "errors": errors,
        "current_stage": "synthesis_complete"
    }

async def output_node(state: dict) -> Dict[str, Any]:
    """Node for generating the final output and investment decision."""
    # Placeholder for output generation logic
    print("Running: output_node")
    
    errors = state.get("errors", [])
    full_report = state.get("full_report")
    investment_decision = state.get("investment_decision")

    if full_report and investment_decision:
        status = "complete"
        print("Workflow completed successfully!")
    elif full_report or investment_decision:
        status = "partial"
        print("Workflow completed with partial results")
    else:
        status = "failed"
        print("Workflow failed")

    if errors:
        print(f"Total errors encountered: {len(errors)}")
    return {"current_stage": status}