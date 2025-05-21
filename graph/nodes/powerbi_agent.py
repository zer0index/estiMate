"""
Power BI Agent node: Specialized feature extraction for PowerBI components.
"""
from typing import Any
from graph.utils.utils import save_to_cache, clean_llm_json, load_from_cache
import yaml
import os
import json
from graph.schemas.strategic_overview import AppComponent
from graph.utils.llm import call_llm

def load_powerbi_prompt():
    PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/powerbi_agent.yaml")
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def summarize_solution_structure(mvp_components, exclude_idx=None):
    summary = []
    for idx, comp in enumerate(mvp_components):
        if exclude_idx is not None and idx == exclude_idx:
            continue
        if hasattr(comp, 'app_name'):
            summary.append({
                'type': 'app',
                'name': comp.app_name,
                'app_type': getattr(comp, 'app_type', None),
                'screens': [
                    {
                        'screen_name': s.screen_name,
                        'features': s.features
                    } for s in getattr(comp, 'app_screens', [])
                ]
            })
    return summary

def find_relevant_chunk_content(prd_chunks):
    # For PowerBI, just collect all chunks with 'PowerBI' in the title or type
    relevant_chunks = []
    for chunk in prd_chunks:
        title = chunk.title.lower() if hasattr(chunk, 'title') else chunk.get('title', '').lower()
        if 'powerbi' in title or getattr(chunk, 'type', '').lower() == 'powerbi':
            relevant_chunks.append(chunk.content if hasattr(chunk, 'content') else chunk.get('content', ''))
    return "\n\n".join(relevant_chunks)

def powerbi_agent(state: Any) -> Any:
    """
    Processes a single PowerBI component, extracting features using LLM.
    Updates the state with the new features for that component.
    """
    # Find the first unprocessed PowerBI component
    solution = getattr(state, "strategic_context", None)
    if not solution:
        print("[PowerBIAgent] No strategic context found in state.")
        return state
    mvp_components = getattr(solution, "mvp_components", [])
    comp = None
    comp_index = None
    for idx, c in enumerate(mvp_components):
        if getattr(c, "app_type", None) == "PowerBI" and not getattr(c, "processed", False):
            comp = c
            comp_index = idx
            break
    if comp is None:
        print("[PowerBIAgent] No unprocessed PowerBI component found.")
        return state
    # Check for cached output
    cached = load_from_cache("powerbi_agent")
    if cached:
        print("[Cache] Using cached output for node 'powerbi_agent'")
        state.strategic_context = cached.get("strategic_context", state.strategic_context)
        # Mark as processed
        mvp_components[comp_index].processed = True
        solution.mvp_components = mvp_components
        state.strategic_context = solution
        return state
    comp_dict = comp.model_dump() if hasattr(comp, "model_dump") else dict(comp)
    parent_component = comp_dict.copy()
    prd_chunks = getattr(state, "chunks", [])
    project_goal = getattr(solution, "purpose", "")
    business_value = getattr(solution, "business_value", [])
    summary = summarize_solution_structure(mvp_components, exclude_idx=comp_index)
    prompt_yaml = load_powerbi_prompt()
    system_message = prompt_yaml.get("system_message", "")
    user_template = prompt_yaml["user_template"]
    chunk_content = find_relevant_chunk_content(prd_chunks)
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
        if "features" in data and data["features"]:
            comp_dict["features"] = data["features"]
    except Exception as e:
        print(f"[Error] Failed to parse LLM output for PowerBI '{comp_dict.get('app_name', '')}': {e}")
        print(f"[Debug] Raw LLM response for PowerBI '{comp_dict.get('app_name', '')}':\n{llm_response}\n")
    # Update the component in the state
    comp_dict["processed"] = True
    mvp_components[comp_index] = AppComponent(**comp_dict)
    solution.mvp_components = mvp_components
    state.strategic_context = solution
    save_to_cache("powerbi_agent", solution)
    print("Power BI Agent: feature extraction complete.")
    return state 