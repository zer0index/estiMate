"""
Component Router node: Routes each MVP component to the correct specialized agent node based on its type.
"""
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.markdown import Markdown
from graph.utils.log import log_info, log_error

console = Console()

def component_router(state: Any) -> Any:
    """
    Updates the state with the next component_index to process, if any.
    """
    log_info("Component Router node: routing MVP components to specialized agents...")
    solution = getattr(state, "strategic_context", None)
    if not solution:
        log_error("No strategic context found in state.")
        log_error("[Router] Returning next: END")
        return state
    mvp_components = getattr(solution, "mvp_components", [])
    for idx, comp in enumerate(mvp_components):
        comp_type = getattr(comp, "app_type", getattr(comp, "flow_type", None))
        if comp_type in ("CanvasApp", "PowerAutomate", "Flow") and not getattr(comp, "processed", False):
            # Route to the first unprocessed component (no need to update state)
            return state
    # If all are processed, just return state (router_conditional will return END)
    return state

def router_conditional(state: Any) -> str:
    solution = getattr(state, "strategic_context", None)
    if not solution:
        return "END"
    mvp_components = getattr(solution, "mvp_components", [])
    # Find the first unprocessed component
    for comp in mvp_components:
        comp_type = getattr(comp, "app_type", getattr(comp, "flow_type", None))
        if not getattr(comp, "processed", False):
            if comp_type == "CanvasApp":
                return "canvas_app_agent"
            elif comp_type == "ModelDrivenApp":
                return "model_driven_agent"
            elif comp_type in ("PowerAutomate", "Flow"):
                return "power_automate_agent"
            elif comp_type == "PowerBI":
                return "powerbi_agent"
    # If all are processed, go to database_node
    return "database_node"