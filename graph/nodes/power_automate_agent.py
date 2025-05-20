"""
Power Automate Agent node: Extracts actions and required connectors for Power Automate/Flow components.
"""
from typing import Any
from graph.utils.utils import save_to_cache, clean_llm_json, load_from_cache
import yaml
import os
import json
from graph.schemas.strategic_overview import FlowComponent
from graph.utils.llm import call_llm

def load_power_automate_prompt():
    PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/power_automate_agent.yaml")
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def power_automate_agent(state: Any) -> Any:
    """
    Processes a single Power Automate/Flow component, extracting actions and connectors.
    Updates the state with the new actions and connectors for that component.
    """
    # Find the first unprocessed PowerAutomate/Flow component
    solution = getattr(state, "strategic_context", None)
    if not solution:
        print("[PowerAutomateAgent] No strategic context found in state.")
        return state
    mvp_components = getattr(solution, "mvp_components", [])
    comp = None
    comp_index = None
    for idx, c in enumerate(mvp_components):
        if getattr(c, "flow_type", None) == "PowerAutomate" and not getattr(c, "processed", False):
            comp = c
            comp_index = idx
            break
    if comp is None:
        print("[PowerAutomateAgent] No unprocessed PowerAutomate component found.")
        return state
    # Check for cached output
    cached = load_from_cache("power_automate_agent")
    if cached:
        print("[Cache] Using cached output for node 'power_automate_agent'")
        state.strategic_context = cached.get("strategic_context", state.strategic_context)
        # Mark as processed
        mvp_components[comp_index].processed = True
        solution.mvp_components = mvp_components
        state.strategic_context = solution
        return state
    comp_dict = comp.model_dump() if hasattr(comp, "model_dump") else dict(comp)
    parent_component = comp_dict.copy()
    parent_component.pop("flow_actions", None)
    prd_chunks = getattr(state, "chunks", [])
    project_goal = getattr(solution, "purpose", "")
    business_value = getattr(solution, "business_value", [])
    summary = []  # Optionally implement a summary function as in canvas_app_agent
    prompt_yaml = load_power_automate_prompt()
    system_message = prompt_yaml.get("system_message", "")
    user_template = prompt_yaml["user_template"]
    if "flow_actions" in comp_dict:
        chunk_content = ""
        user_prompt = user_template \
            .replace("{{ project_goal }}", project_goal) \
            .replace("{{ business_value }}", json.dumps(business_value, ensure_ascii=False)) \
            .replace("{{ solution_summary }}", json.dumps(summary, ensure_ascii=False, indent=2)) \
            .replace("{{ parent_component }}", json.dumps(parent_component, ensure_ascii=False, indent=2)) \
            .replace("{{ current_item }}", json.dumps(comp_dict, ensure_ascii=False, indent=2)) \
            .replace("{{ chunk_content }}", chunk_content)
        llm_response = call_llm(
            prompt=user_prompt,
            model="gpt-4-1106-preview",
            temperature=0.2,
            system_message=system_message
        )
        try:
            cleaned_response = clean_llm_json(llm_response)
            data = json.loads(cleaned_response)
            comp_dict["trigger"] = data.get("trigger", "")
            comp_dict["actions"] = data.get("actions", {})
            comp_dict["connectors"] = data.get("connectors", {})
        except Exception as e:
            print(f"[Error] Failed to parse LLM output for flow '{comp_dict.get('flow_name', '')}': {e}")
            print(f"[Debug] Raw LLM response for flow '{comp_dict.get('flow_name', '')}':\n{llm_response}\n")
            comp_dict["trigger"] = ""
            comp_dict["actions"] = {}
            comp_dict["connectors"] = {}
    # Update the component in the state
    comp_dict["processed"] = True
    mvp_components[comp_index] = FlowComponent(**comp_dict)
    solution.mvp_components = mvp_components
    state.strategic_context = solution
    print("[Debug] Updated strategic_context:", state.strategic_context.model_dump() if hasattr(state.strategic_context, 'model_dump') else state.strategic_context)
    save_to_cache("power_automate_agent", solution)
    print("[PowerAutomateAgent] Action and connector extraction complete.")
    return state 