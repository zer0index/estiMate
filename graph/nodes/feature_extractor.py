"""
Feature Extractor node: Extracts features from PRD chunks and assigns them to the correct app screen or flow action.
"""
from typing import Any
from graph.llm import call_llm
from graph.utils import save_to_cache, load_from_cache, clean_llm_json
import yaml
import os
import json
from graph.schemas.strategic_overview import AppComponent, FlowComponent

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/feature_extractor.yaml")

# Helper to load and render the prompt
def load_prompt():
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def coerce_mvp_component(comp: dict):
    # Normalize features for app_screens and flow_actions to ensure dict or None
    if "app_name" in comp and "app_screens" in comp:
        for screen in comp["app_screens"]:
            features = screen.get("features")
            if features is not None and not isinstance(features, dict):
                screen["features"] = None  # fallback if LLM returns wrong type
        return AppComponent(**comp)
    elif "flow_name" in comp and "flow_actions" in comp:
        for action in comp["flow_actions"]:
            features = action.get("features")
            if features is not None and not isinstance(features, dict):
                action["features"] = None  # fallback if LLM returns wrong type
        return FlowComponent(**comp)
    else:
        raise ValueError("Unknown MVP component type: {}".format(comp))

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
        elif hasattr(comp, 'flow_name'):
            summary.append({
                'type': 'flow',
                'name': comp.flow_name,
                'flow_type': getattr(comp, 'flow_type', None),
                'actions': [
                    {
                        'action_name': a.action_name,
                        'features': a.features
                    } for a in getattr(comp, 'flow_actions', [])
                ]
            })
    return summary

def find_relevant_chunk_content(component, prd_chunks):
    """
    Find the most relevant PRD chunk(s) for a given component by matching titles.
    If multiple chunks are relevant, concatenate their content.
    """
    name = getattr(component, 'app_name', getattr(component, 'flow_name', None))
    if not name:
        return ""
    # Simple heuristic: match chunk titles containing key words from the component name or type
    relevant_chunks = []
    for chunk in prd_chunks:
        title = chunk.title.lower() if hasattr(chunk, 'title') else chunk.get('title', '').lower()
        if name.lower() in title:
            relevant_chunks.append(chunk.content if hasattr(chunk, 'content') else chunk.get('content', ''))
    # If no direct match, fallback to all feature-related chunks
    if not relevant_chunks:
        for chunk in prd_chunks:
            title = chunk.title.lower() if hasattr(chunk, 'title') else chunk.get('title', '').lower()
            if any(word in title for word in ["feature", "mvp", "post-mvp", "workflow", "screen", "automation"]):
                relevant_chunks.append(chunk.content if hasattr(chunk, 'content') else chunk.get('content', ''))
    # Fallback: use all chunks
    if not relevant_chunks:
        relevant_chunks = [chunk.content if hasattr(chunk, 'content') else chunk.get('content', '') for chunk in prd_chunks]
    return "\n\n".join(relevant_chunks)

def feature_extractor(state: Any) -> Any:
    """
    Loops over all MVP components (apps/flows), then over each screen/action, extracts features, and updates the solution structure in state using chunking.
    """
    print("Feature Extractor node: checking cache...")
    
    # Try to load from cache first
    cached_data = load_from_cache("feature_extractor")
    if cached_data is not None:
        print("Feature Extractor node: using cached output")
        state.strategic_context = cached_data
        return state

    print("Feature Extractor node: extracting features from MVP components (per screen/action chunked)...")
    solution = getattr(state, "strategic_context", None)
    if not solution:
        print("[Error] No strategic context found in state.")
        return state

    prompt_yaml = load_prompt()
    system_message = prompt_yaml.get("system_message", "")
    user_template = prompt_yaml["user_template"]

    project_goal = getattr(solution, "purpose", "")
    business_value = getattr(solution, "business_value", [])
    mvp_components = getattr(solution, "mvp_components", [])
    prd_chunks = getattr(state, "chunks", [])

    # For each app/flow, process each screen/action as a chunk
    updated_components = []
    for idx, comp in enumerate(mvp_components):
        summary = summarize_solution_structure(mvp_components, exclude_idx=idx)
        comp_dict = comp.model_dump() if hasattr(comp, "model_dump") else dict(comp)
        parent_component = comp_dict.copy()
        # Remove screens/actions from parent for brevity
        parent_component.pop("app_screens", None)
        parent_component.pop("flow_actions", None)
        if "app_screens" in comp_dict:
            for sidx, screen in enumerate(comp_dict["app_screens"]):
                chunk_content = find_relevant_chunk_content(screen, prd_chunks)
                print(f"\n[DEBUG] Processing app screen {sidx+1}/{len(comp_dict['app_screens'])} of component {idx+1}/{len(mvp_components)}: {screen.get('screen_name')}")
                print(f"[DEBUG] Chunk content (first 500 chars):\n{chunk_content[:500]}")
                user_prompt = user_template \
                    .replace("{{ project_goal }}", project_goal) \
                    .replace("{{ business_value }}", json.dumps(business_value, ensure_ascii=False)) \
                    .replace("{{ solution_summary }}", json.dumps(summary, ensure_ascii=False, indent=2)) \
                    .replace("{{ parent_component }}", json.dumps(parent_component, ensure_ascii=False, indent=2)) \
                    .replace("{{ current_item }}", json.dumps(screen, ensure_ascii=False, indent=2)) \
                    .replace("{{ chunk_content }}", chunk_content)
                llm_response = call_llm(
                    prompt=user_prompt,
                    model="gpt-4-1106-preview",
                    temperature=0.2,
                    system_message=system_message
                )
                print(f"[DEBUG] LLM response (first 500 chars):\n{llm_response[:500]}")
                try:
                    cleaned_response = clean_llm_json(llm_response)
                    data = json.loads(cleaned_response)
                    if "features" in data and data["features"]:
                        screen["features"] = data["features"]
                    if "sota_suggestions" in data and data["sota_suggestions"]:
                        screen["sota_suggestions"] = data["sota_suggestions"]
                except Exception as e:
                    print(f"[Error] Failed to parse LLM output for screen '{screen.get('screen_name', '')}': {e}")
                    print(f"[Debug] Raw LLM response for screen '{screen.get('screen_name', '')}':\n{llm_response}\n")
        elif "flow_actions" in comp_dict:
            for aidx, action in enumerate(comp_dict["flow_actions"]):
                chunk_content = find_relevant_chunk_content(action, prd_chunks)
                print(f"\n[DEBUG] Processing flow action {aidx+1}/{len(comp_dict['flow_actions'])} of component {idx+1}/{len(mvp_components)}: {action.get('action_name')}")
                print(f"[DEBUG] Chunk content (first 500 chars):\n{chunk_content[:500]}")
                user_prompt = user_template \
                    .replace("{{ project_goal }}", project_goal) \
                    .replace("{{ business_value }}", json.dumps(business_value, ensure_ascii=False)) \
                    .replace("{{ solution_summary }}", json.dumps(summary, ensure_ascii=False, indent=2)) \
                    .replace("{{ parent_component }}", json.dumps(parent_component, ensure_ascii=False, indent=2)) \
                    .replace("{{ current_item }}", json.dumps(action, ensure_ascii=False, indent=2)) \
                    .replace("{{ chunk_content }}", chunk_content)
                llm_response = call_llm(
                    prompt=user_prompt,
                    model="gpt-4-1106-preview",
                    temperature=0.2,
                    system_message=system_message
                )
                print(f"[DEBUG] LLM response (first 500 chars):\n{llm_response[:500]}")
                try:
                    cleaned_response = clean_llm_json(llm_response)
                    data = json.loads(cleaned_response)
                    if "features" in data and data["features"]:
                        action["features"] = data["features"]
                    if "sota_suggestions" in data and data["sota_suggestions"]:
                        action["sota_suggestions"] = data["sota_suggestions"]
                except Exception as e:
                    print(f"[Error] Failed to parse LLM output for action '{action.get('action_name', '')}': {e}")
                    print(f"[Debug] Raw LLM response for action '{action.get('action_name', '')}':\n{llm_response}\n")
        updated_components.append(coerce_mvp_component(comp_dict))

    solution.mvp_components = updated_components
    state.strategic_context = solution
    save_to_cache("feature_extractor", solution)
    print("Feature extraction complete.")
    return state 