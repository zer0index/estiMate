"""
Strategic Overview node: Extracts and processes the strategic overview section from PRD chunks.
"""
from typing import Any
from graph.schemas.strategic_overview import StrategicContext
from graph.utils.llm import call_llm
from graph.utils.utils import save_to_cache, load_from_cache
from graph.utils.log import log_info, log_success, log_warning, log_error
import yaml
import os
import re
import json
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.markdown import Markdown

console = Console()

def render_prompt(chunks, prompt_path):
    """Render the YAML prompt with the PRD chunks."""
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_yaml = yaml.safe_load(f)
    user_template = prompt_yaml["user_template"]
    # Simple rendering: replace {{ chunk.title }} and {{ chunk.content }}
    # For now, join all chunks as sections
    sections = []
    for chunk in chunks:
        sections.append(f"--- SECTION: {getattr(chunk, 'title', '')} ---\n{getattr(chunk, 'content', '')}\n")
    rendered = user_template.replace(
        '{% for chunk in chunks %}\n--- SECTION: {{ chunk.title }} ---\n{{ chunk.content }}\n\n{% endfor %}',
        "\n".join(sections)
    )
    return prompt_yaml.get("system_message", ""), rendered

def extract_json_from_response(response: str) -> str:
    """Extract JSON object from LLM response, handling triple backticks and extra text."""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"(\{.*\})", response, re.DOTALL)
    if match:
        return match.group(1)
    return response.strip()

def clean_llm_json(text: str) -> str:
    """Clean LLM JSON output: remove code fences, comments, and trailing commas."""
    text = re.sub(r'```(?:json)?', '', text)
    text = re.sub(r'//.*', '', text)
    text = re.sub(r',([ \t\r\n]*[}\]])', r'\1', text)
    return text.strip()

def fix_component_types(json_str):
    """Map invalid component types to 'Other' for mvp_components and post_mvp_modules."""
    allowed = {"CanvasApp", "ModelDrivenApp", "PowerAutomate", "PowerPages", "PowerBI", "CustomConnector", "Other"}
    try:
        data = json.loads(json_str)
        for section in ["mvp_components", "post_mvp_modules"]:
            if section in data and isinstance(data[section], list):
                for comp in data[section]:
                    if isinstance(comp, dict) and comp.get("type") and comp.get("type") not in allowed:
                        comp["type"] = "Other"
        return json.dumps(data)
    except Exception as e:
        log_warning(f"Could not post-process component types: {e}")
        return json_str

def strategic_overview(state: Any) -> Any:
    """
    Extracts the strategic overview from PRD chunks using an LLM and validates output with StrategicContext schema.
    Writes the result to memory/strategic_context.json.
    """
    # Use rich for status output
    log_info("Strategic Overview node: checking cache...")
    
    # Try to load from cache first
    cached_data = load_from_cache("strategic_overview")
    if cached_data is not None:
        log_success("[Cache] Strategic Overview node: using cached output")
        # Convert dict back to StrategicContext
        context = StrategicContext.parse_obj(cached_data)
        state.strategic_context = context
        return state

    log_warning("Strategic Overview node: extracting strategic context from PRD chunks...")
    chunks = getattr(state, "chunks", [])
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/strategic_overview.yaml")
    system_message, user_prompt = render_prompt(chunks, prompt_path)
    # Node-specific LLM config
    model = "gpt-4-1106-preview"
    temperature = 0.2
    # Call the LLM
    llm_response = call_llm(
        prompt=user_prompt,
        model=model,
        temperature=temperature,
        system_message=system_message
    )
    # Log raw LLM output for debugging
    try:
        with open("memory/strategic_overview_llm_raw.json", "w", encoding="utf-8") as f:
            f.write(llm_response)
    except Exception as log_exc:
        log_warning(f"Could not log raw LLM output: {log_exc}")
    # Clean, post-process, and parse response
    try:
        cleaned = extract_json_from_response(llm_response)
        cleaned = clean_llm_json(cleaned)
        fixed = fix_component_types(cleaned)
        context = StrategicContext.parse_raw(fixed)

        # --- Merge all CanvasApp MVP components into a single app ---
        canvas_apps = [c for c in context.mvp_components if hasattr(c, 'app_type') and getattr(c, 'app_type', None) == 'CanvasApp']
        if len(canvas_apps) > 1:
            # Merge screens and details
            merged_screens = []
            merged_details = []
            app_names = []
            for app in canvas_apps:
                merged_screens.extend(getattr(app, 'app_screens', []))
                merged_details.append(getattr(app, 'app_details', ''))
                app_names.append(getattr(app, 'app_name', ''))
            # Heuristic: if all names are the same, use it; if not, join unique names
            unique_names = list(dict.fromkeys([n for n in app_names if n]))
            if len(unique_names) == 1:
                merged_name = unique_names[0]
            elif any('Order' in n for n in unique_names):
                merged_name = next((n for n in unique_names if 'Order' in n), unique_names[0])
            else:
                merged_name = ' / '.join(unique_names)
            merged_app = type(canvas_apps[0])( # AppComponent
                app_name=merged_name,
                app_type='CanvasApp',
                app_details=' '.join(merged_details),
                app_screens=merged_screens,
                processed=False
            )
            # Remove all CanvasApp apps and insert the merged one at the start
            context.mvp_components = [c for c in context.mvp_components if not (hasattr(c, 'app_type') and getattr(c, 'app_type', None) == 'CanvasApp')]
            context.mvp_components.insert(0, merged_app)

        state.strategic_context = context
        save_to_cache("strategic_overview", context)
        log_success("Strategic context extracted, validated, and saved to cache.")
    except Exception as e:
        log_error(f"Failed to parse LLM output: {e}")
        # Attempt a simple auto-fix: fix missing commas between objects in arrays, close unclosed braces/brackets at the END, and retry once
        try:
            fixed2 = cleaned.rstrip()
            # Fix missing commas between objects in arrays (e.g., ...}{... → ...},{...)
            fixed2 = re.sub(r'}\s*{', '},\n{', fixed2)
            # Only add closing brackets/braces at the end if missing
            open_braces = fixed2.count('{')
            close_braces = fixed2.count('}')
            open_brackets = fixed2.count('[')
            close_brackets = fixed2.count(']')
            if close_braces < open_braces:
                fixed2 = fixed2 + ('}' * (open_braces - close_braces))
            if close_brackets < open_brackets:
                fixed2 = fixed2 + (']' * (open_brackets - close_brackets))
            fixed2 = fix_component_types(fixed2)
            context = StrategicContext.parse_raw(fixed2)
            state.strategic_context = context
            save_to_cache("strategic_overview", context)
            log_warning("Strategic context auto-fixed and parsed after initial failure (comma/truncation fix).")
        except Exception as e2:
            log_error(f"Strategic Overview node failed after auto-fix: {e2}")
    return state