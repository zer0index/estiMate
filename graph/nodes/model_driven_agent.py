"""
Model Driven App Agent node: Specialized feature extraction for ModelDrivenApp components.
"""
from typing import Any
from graph.utils.utils import save_to_cache, clean_llm_json, load_from_cache
import yaml
import os
import json
from graph.schemas.strategic_overview import AppComponent
from graph.utils.llm import call_llm
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.markdown import Markdown
from graph.utils.log import log_info, log_success, log_warning, log_error

console = Console()

def load_model_driven_prompt():
    PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/model_driven_agent.yaml")
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def render_model_driven_prompt(project_goal, business_value, solution_summary, parent_component, screen, chunk_content, prompt_yaml):
    user_template = prompt_yaml["user_template"]
    # Render business value as bullet list
    business_value_str = "\n".join(f"- {item}" for item in business_value)
    # Render the template
    prompt = user_template \
        .replace("{{ project_goal }}", project_goal) \
        .replace("{{ solution_summary }}", solution_summary) \
        .replace("{{ parent_component }}", json.dumps(parent_component, ensure_ascii=False, indent=2)) \
        .replace("{{ current_item }}", json.dumps(screen, ensure_ascii=False, indent=2)) \
        .replace("{{ chunk_content }}", chunk_content) \
        .replace("{% for item in business_value %}\n- {{ item }}\n{% endfor %}", business_value_str)
    return prompt_yaml.get("system_message", ""), prompt

def find_relevant_chunk_content(screen, prd_chunks):
    name = screen.get('screen_name', None)
    if not name:
        return ""
    relevant_chunks = []
    for chunk in prd_chunks:
        title = chunk.title.lower() if hasattr(chunk, 'title') else chunk.get('title', '').lower()
        if name.lower() in title:
            relevant_chunks.append(chunk.content if hasattr(chunk, 'content') else chunk.get('content', ''))
    if not relevant_chunks:
        for chunk in prd_chunks:
            title = chunk.title.lower() if hasattr(chunk, 'title') else chunk.get('title', '').lower()
            if any(word in title for word in ["feature", "mvp", "screen"]):
                relevant_chunks.append(chunk.content if hasattr(chunk, 'content') else chunk.get('content', ''))
    if not relevant_chunks:
        relevant_chunks = [chunk.content if hasattr(chunk, 'content') else chunk.get('content', '') for chunk in prd_chunks]
    return "\n\n".join(relevant_chunks)

def flatten_features(features):
    if not isinstance(features, dict):
        return features
    flat = {}
    for k, v in features.items():
        if isinstance(v, dict):
            # Convert nested dict to a string description
            flat[k] = ", ".join(f"{subk}: {subv}" for subk, subv in v.items())
        else:
            flat[k] = v
    return flat

def model_driven_agent(state: Any) -> Any:
    """
    Processes a single ModelDrivenApp component, extracting features per screen using LLM.
    Updates the state with the new features for that component.
    """
    # Find the first unprocessed ModelDrivenApp component
    solution = getattr(state, "strategic_context", None)
    if not solution:
        log_error("[ModelDrivenAgent] No strategic context found in state.")
        return state
    mvp_components = getattr(solution, "mvp_components", [])
    comp = None
    comp_index = None
    for idx, c in enumerate(mvp_components):
        if getattr(c, "app_type", None) == "ModelDrivenApp" and not getattr(c, "processed", False):
            comp = c
            comp_index = idx
            break
    if comp is None:
        log_warning("[ModelDrivenAgent] No unprocessed ModelDrivenApp component found.")
        return state
    # Check for cached output
    cached = load_from_cache("model_driven_agent")
    if cached:
        log_success("[Cache] Using cached output for node 'model_driven_agent'")
        state.strategic_context = cached.get("strategic_context", state.strategic_context)
        # Mark as processed
        mvp_components[comp_index].processed = True
        solution.mvp_components = mvp_components
        state.strategic_context = solution
        return state
    comp_dict = comp.model_dump() if hasattr(comp, "model_dump") else dict(comp)
    parent_component = comp_dict.copy()
    parent_component.pop("app_screens", None)
    prd_chunks = getattr(state, "chunks", [])
    project_goal = getattr(solution, "purpose", "")
    business_value = getattr(solution, "business_value", [])
    solution_summary = ""  # Optionally summarize solution structure
    prompt_yaml = load_model_driven_prompt()
    system_message = prompt_yaml.get("system_message", "")
    # For each screen, call the LLM and parse the response
    if "app_screens" in comp_dict:
        for sidx, screen in enumerate(comp_dict["app_screens"]):
            chunk_content = find_relevant_chunk_content(screen, prd_chunks)
            sys_msg, user_prompt = render_model_driven_prompt(
                project_goal, business_value, solution_summary, parent_component, screen, chunk_content, prompt_yaml
            )
            llm_response = call_llm(
                prompt=user_prompt,
                model="gpt-4-1106-preview",
                temperature=0.2,
                system_message=sys_msg
            )
            try:
                cleaned_response = clean_llm_json(llm_response)
                data = json.loads(cleaned_response)
                if "features" in data and data["features"]:
                    screen["features"] = flatten_features(data["features"])
                if "sota_suggestions" in data:
                    screen["sota_suggestions"] = data["sota_suggestions"]
            except Exception as e:
                log_error(f"[ModelDrivenAgent] Failed to parse LLM output for screen '{screen.get('screen_name', '')}': {e}")
                log_info(f"[ModelDrivenAgent] Raw LLM response for screen '{screen.get('screen_name', '')}':\n{llm_response}\n")
    # Update the component in the state
    comp_dict["processed"] = True
    mvp_components[comp_index] = AppComponent(**comp_dict)
    solution.mvp_components = mvp_components
    state.strategic_context = solution
    save_to_cache("model_driven_agent", solution)
    # Use rich for status output
    log_success("Model Driven Agent: feature extraction complete.")
    return state