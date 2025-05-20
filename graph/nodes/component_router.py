"""
Component Router node: Routes each MVP component to the correct specialized agent node based on its type.
"""
from typing import Any

def component_router(state: Any) -> Any:
    """
    Updates the state with the next component_index to process, if any.
    """
    print("Component Router node: routing MVP components to specialized agents...")
    solution = getattr(state, "strategic_context", None)
    if not solution:
        print("[Error] No strategic context found in state.")
        print("[Router] Returning next: END")
        return state
    mvp_components = getattr(solution, "mvp_components", [])
    for idx, comp in enumerate(mvp_components):
        comp_type = getattr(comp, "app_type", getattr(comp, "flow_type", None))
        if comp_type in ("CanvasApp", "PowerAutomate", "Flow"):
            # Only set component_index for the first unprocessed component
            if getattr(state, "component_index", None) != idx:
                new_state = state.copy(update={"component_index": idx})
                return new_state
    # If no more components, just return state (component_index unchanged or None)
    return state

def router_conditional(state: Any) -> str:
    solution = getattr(state, "strategic_context", None)
    if not solution:
        return "END"
    mvp_components = getattr(solution, "mvp_components", [])
    component_index = getattr(state, "component_index", None)
    if component_index is None or component_index >= len(mvp_components):
        return "END"
    comp = mvp_components[component_index]
    comp_type = getattr(comp, "app_type", getattr(comp, "flow_type", None))
    if comp_type == "CanvasApp":
        return "canvas_app_agent"
    elif comp_type in ("PowerAutomate", "Flow"):
        return "power_automate_agent"
    else:
        return "END" 