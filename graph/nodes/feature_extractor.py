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

def feature_extractor(state: Any) -> Any:
    """
    Loops over all PRD chunks, extracts features, and updates the solution structure in state.
    """
    print("Feature Extractor node: checking cache...")
    
    # Try to load from cache first
    cached_data = load_from_cache("feature_extractor")
    if cached_data is not None:
        print("Feature Extractor node: using cached output")
        state.strategic_context = cached_data
        return state

    print("Feature Extractor node: extracting features from PRD chunks...")
    chunks = getattr(state, "chunks", [])
    # Assume strategic_context is already in state
    solution = getattr(state, "strategic_context", None)
    if not solution:
        print("[Error] No strategic context found in state.")
        return state
    
    prompt_yaml = load_prompt()
    system_message = prompt_yaml.get("system_message", "")
    user_template = prompt_yaml["user_template"]
    
    # Loop over chunks and update features
    for chunk in chunks:
        # Render the user prompt
        solution_json = json.dumps(solution.model_dump(), ensure_ascii=False, indent=2)
        user_prompt = user_template.replace("{{ chunk.title }}", getattr(chunk, "title", "")).replace("{{ chunk.content }}", getattr(chunk, "content", "")).replace("{{ solution_structure }}", solution_json)
        llm_response = call_llm(
            prompt=user_prompt,
            model="gpt-4-1106-preview",
            temperature=0.2,
            system_message=system_message
        )
        # Clean and parse the LLM response
        try:
            cleaned_response = clean_llm_json(llm_response)
            data = json.loads(cleaned_response)
            # Coerce each mvp_component to the correct Pydantic model
            mvp_components = data.get("mvp_components", solution.mvp_components)
            solution.mvp_components = [coerce_mvp_component(comp) for comp in mvp_components]
            # (For now, just overwrite; in production, merge features)
        except Exception as e:
            print(f"[Error] Failed to parse LLM output for chunk '{getattr(chunk, 'title', '')}': {e}")
            print(f"[Debug] Raw LLM response for chunk '{getattr(chunk, 'title', '')}':\n{llm_response}\n")
    
    state.strategic_context = solution
    
    # Save to cache
    save_to_cache("feature_extractor", solution)
    
    print("Feature extraction complete.")
    return state 