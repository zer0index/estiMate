"""
Merge Agent node: Merges all relevant outputs from the DAG into a single, well-structured JSON object for downstream estimation.
"""
from typing import Any
import json
import os
from graph.utils.utils import save_to_cache, load_from_cache
from rich.console import Console

console = Console()

MERGED_OUTPUT_PATH = os.path.join("memory", "merge_agent_output.json")


def merge_agent(state: Any) -> Any:
    """
    Merges all relevant pipeline outputs into a single JSON object and saves it.
    Extensible: will include any additional agent outputs present in the state.
    Also merges features from agent outputs into the strategic_overview structure.
    """
    import glob
    # Check for cached output
    if os.path.exists(MERGED_OUTPUT_PATH):
        console.print(f"[Cache] Using cached output for node 'merge_agent' at {MERGED_OUTPUT_PATH}")
        with open(MERGED_OUTPUT_PATH, "r", encoding="utf-8") as f:
            merged = json.load(f)
        state.merged_output = merged
        return state

    # Gather all relevant info from state
    merged = {}
    # Strategic context (includes MVP components, post-MVP modules, roles, constraints, etc.)
    strategic_context = getattr(state, "strategic_context", None)
    if strategic_context:
        # Convert to dict for easier manipulation
        strategic_dict = json.loads(strategic_context.model_dump_json() if hasattr(strategic_context, "model_dump_json") else json.dumps(strategic_context, default=str))
        # --- Merge features from agent outputs ---
        # Find all *_agent_output.json files in memory/
        agent_outputs = {}
        for path in glob.glob(os.path.join("memory", "*_agent_output.json")):
            agent_name = os.path.basename(path).replace("_output.json", "")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    agent_outputs[agent_name] = json.load(f)
                console.print(f"[MergeAgent][DEBUG] Loaded agent output: {agent_name}")
            except Exception as e:
                console.print(f"[MergeAgent][DEBUG] Failed to load {agent_name}: {e}")
                continue
        # Merge features for CanvasApp, ModelDrivenApp, PowerAutomate, PowerBI
        mvp_components = strategic_dict.get("mvp_components", [])
        for comp in mvp_components:
            # CanvasApp/ModelDrivenApp/PowerBI: merge features into app_screens
            if comp.get("app_type") in ("CanvasApp", "ModelDrivenApp", "PowerBI"):
                # Use correct agent key naming (e.g., 'canvas_app_agent')
                app_type = comp['app_type'].lower()
                if app_type == "canvasapp":
                    agent_key = "canvas_app_agent"
                elif app_type == "modeldrivenapp":
                    agent_key = "model_driven_agent"
                elif app_type == "powerbi":
                    agent_key = "powerbi_agent"
                else:
                    agent_key = f"{app_type}_agent"
                agent_data = agent_outputs.get(agent_key)
                console.print(f"[MergeAgent][DEBUG] Matching app: {comp.get('app_name')} (agent_key: {agent_key})")
                if agent_data and "mvp_components" in agent_data:
                    for agent_comp in agent_data["mvp_components"]:
                        console.print(f"[MergeAgent][DEBUG]   Agent app: {agent_comp.get('app_name')}")
                        if agent_comp.get("app_name", "").strip().lower() == comp.get("app_name", "").strip().lower():
                            for screen in comp.get("app_screens", []):
                                console.print(f"[MergeAgent][DEBUG]     Matching screen: {screen.get('screen_name')}")
                                for agent_screen in agent_comp.get("app_screens", []):
                                    console.print(f"[MergeAgent][DEBUG]       Agent screen: {agent_screen.get('screen_name')}")
                                    if agent_screen.get("screen_name", "").strip().lower() == screen.get("screen_name", "").strip().lower() and agent_screen.get("features"):
                                        screen["features"] = agent_screen["features"]
                                        console.print(f"[MergeAgent][DEBUG]       Merged features for screen: {screen['screen_name']}")
            # PowerAutomate: merge features into flow_actions and copy actions/connectors/trigger
            if comp.get("flow_type") == "PowerAutomate":
                agent_data = agent_outputs.get("power_automate_agent")
                console.print(f"[MergeAgent][DEBUG] Matching flow: {comp.get('flow_name')}")
                if agent_data and "mvp_components" in agent_data:
                    for agent_comp in agent_data["mvp_components"]:
                        console.print(f"[MergeAgent][DEBUG]   Agent flow: {agent_comp.get('flow_name')}")
                        if agent_comp.get("flow_name", "").strip().lower() == comp.get("flow_name", "").strip().lower():
                            # Merge features for each action
                            for action in comp.get("flow_actions", []):
                                console.print(f"[MergeAgent][DEBUG]     Matching action: {action.get('action_name')}")
                                for agent_action in agent_comp.get("flow_actions", []):
                                    console.print(f"[MergeAgent][DEBUG]       Agent action: {agent_action.get('action_name')}")
                                    if agent_action.get("action_name", "").strip().lower() == action.get("action_name", "").strip().lower() and agent_action.get("features"):
                                        action["features"] = agent_action["features"]
                                        console.print(f"[MergeAgent][DEBUG]       Merged features for flow action: {action['action_name']}")
                            # Copy top-level actions/connectors/trigger if present
                            for key in ("actions", "connectors", "trigger"):
                                if agent_comp.get(key) is not None:
                                    comp[key] = agent_comp[key]
                                    console.print(f"[MergeAgent][DEBUG]       Merged {key} for flow: {comp.get('flow_name')}")
        strategic_dict["mvp_components"] = mvp_components
        merged["strategic_overview"] = strategic_dict
    # Database model
    database_model = getattr(state, "database_model", None)
    if database_model:
        merged["database_model"] = json.loads(database_model.model_dump_json() if hasattr(database_model, "model_dump_json") else json.dumps(database_model, default=str))
    # Merge any additional agent outputs present in state (future extensibility)
    for key, value in state.__dict__.items():
        if key in merged or key.startswith("_") or key in ("strategic_context", "database_model", "merged_output"):
            continue
        # Only include serializable objects
        try:
            json.dumps(value)
            merged[key] = value
        except Exception:
            try:
                merged[key] = json.loads(value.model_dump_json()) if hasattr(value, "model_dump_json") else str(value)
            except Exception:
                merged[key] = str(value)
    # Save to file (pretty-printed)
    with open(MERGED_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    state.merged_output = merged
    # Also save to cache (for consistency with other agents)
    save_to_cache("merge_agent", merged)
    console.print(f"[MergeAgent] Merged output written to {MERGED_OUTPUT_PATH}")
    return state
