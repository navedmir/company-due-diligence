from langgraph.graph import StateGraph, END
from ..state.schema import DueDiligenceState
from .nodes import init_node, research_node, validate_research_node, analysis_node, synthesis_node, output_node
from .routing import check_init_success, check_research_completeness

def create_due_diligence_graph() -> StateGraph:
    """Create a state graph for the due diligence workflow."""
    workflow = StateGraph(DueDiligenceState)


    workflow.add_node("init", init_node)
    workflow.add_node("research", research_node)
    workflow.add_node("validate_research", validate_research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("output", output_node)

    workflow.set_entry_point("init")
    
    workflow.add_conditional_edges("init", check_init_success, {"success": "research", "failed": "output"} )
    workflow.add_edge("research", "validate_research")
    workflow.add_conditional_edges("validate_research", check_research_completeness, {"complete": "analysis", "incomplete": "research", "failed": "output"} )

    workflow.add_edge("analysis", "synthesis")
    workflow.add_edge("synthesis", "output")
    workflow.add_edge("output", END)
    return workflow


def compile_workflow() -> StateGraph:
    """Compile the due diligence workflow graph."""
    graph = create_due_diligence_graph()
    return graph.compile()

compiled_graph = None

def get_compliled_workflow():
    """Get the compiled workflow graph."""
    global compiled_graph
    if compiled_graph is None:
        complied_graph = compile_workflow()
    print(complied_graph.get_graph().draw_mermaid())
    return complied_graph

async def run_due_diligence(startup_name: str, startup_description: str, funding_stage: str = None) -> DueDiligenceState:
    """Run the due diligence workflow."""
    
    from ..state.schema import create_initial_state

    initial_state = create_initial_state(startup_name=startup_name, startup_description=startup_description, funding_stage=funding_stage)

    graph = get_compliled_workflow()
    final_state = await graph.ainvoke(initial_state)

    return final_state