"""
Strategic Overview node: Extracts and processes the strategic overview section from PRD chunks.
"""
from typing import Any
from graph.schemas.strategic_overview import StrategicContext
from graph.llm import call_llm
import yaml
import os
import re
import json

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

def fix_component_types(json_str):
    """Map invalid component types to 'Other' for mvp_components and post_mvp_modules."""
    allowed = {"CanvasApp", "ModelDrivenApp", "PowerAutomate", "Dataverse", "PowerPages", "CustomConnector", "Other"}
    try:
        data = json.loads(json_str)
        for section in ["mvp_components", "post_mvp_modules"]:
            if section in data and isinstance(data[section], list):
                for comp in data[section]:
                    if comp.get("type") not in allowed:
                        comp["type"] = "Other"
        return json.dumps(data)
    except Exception as e:
        print(f"[Warning] Could not post-process component types: {e}")
        return json_str

def strategic_overview(state: Any) -> Any:
    """
    Extracts the strategic overview from PRD chunks using an LLM and validates output with StrategicContext schema.
    Writes the result to memory/strategic_context.json.
    """
    print("Strategic Overview node: extracting strategic context from PRD chunks...")
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
    # Clean, post-process, and parse response
    try:
        cleaned = extract_json_from_response(llm_response)
        fixed = fix_component_types(cleaned)
        context = StrategicContext.parse_raw(fixed)
        state.strategic_context = context
        # Write output to memory/strategic_context.json
        with open("memory/strategic_context.json", "w", encoding="utf-8") as f:
            json.dump(context.model_dump(), f, ensure_ascii=False, indent=2)
        print("Strategic context extracted, validated, and saved to memory/strategic_context.json.")
    except Exception as e:
        print(f"[Error] Failed to parse LLM output: {e}")
        state.strategic_context = None
    return state 