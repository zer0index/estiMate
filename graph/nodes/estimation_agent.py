"""
Estimation Agent node: Uses LLM and the estimation matrix to estimate effort for each component/screen in the merged output.
"""
import os
import json
import yaml
from typing import Any
from graph.utils.llm import call_llm
from graph.utils.utils import save_to_cache, clean_llm_json
from rich.console import Console

console = Console()

MATRIX_PATH = os.path.join("graph", "matrix", "matrix.json")
ESTIMATION_OUTPUT_PATH = os.path.join("memory", "estimation_agent_output.json")
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/estimation_agent.yaml")

# Helper: Load matrix
with open(MATRIX_PATH, "r", encoding="utf-8") as f:
    MATRIX = json.load(f)["components"]

def get_matrix_section(component_type: str):
    # Normalize keys
    mapping = {
        "CanvasApp": "Canvas App",
        "ModelDrivenApp": "Model Driven App",
        "PowerAutomate": "Power Automate",
        "PowerBI": "Power BI",
        "PowerPages": "Power Pages"
    }
    return MATRIX.get(mapping.get(component_type, component_type), None)

def load_estimation_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        prompt_yaml = yaml.safe_load(f)
    return prompt_yaml["system_message"], prompt_yaml["user_template"]

def estimation_agent(state: Any) -> Any:
    # Check for cached output
    if os.path.exists(ESTIMATION_OUTPUT_PATH):
        console.print(f"[Cache] Using cached output for node 'estimation_agent' at {ESTIMATION_OUTPUT_PATH}")
        with open(ESTIMATION_OUTPUT_PATH, "r", encoding="utf-8") as f:
            estimates = json.load(f)
        state.estimation_output = estimates
        return state

    merged = getattr(state, "merged_output", None)
    if not merged:
        raise ValueError("No merged_output found in state for estimation.")
    strategic = merged["strategic_overview"]
    results = []

    system_message, user_template = load_estimation_prompt()

    # CanvasApp, ModelDrivenApp, PowerPages: per screen
    for comp in strategic.get("mvp_components", []):
        if comp.get("app_type") in ("CanvasApp", "ModelDrivenApp", "PowerPages"):
            matrix_section = get_matrix_section(comp["app_type"])
            for screen in comp.get("app_screens", []):
                obj = {
                    "app_name": comp.get("app_name"),
                    "screen_name": screen.get("screen_name"),
                    "screen_type": screen.get("screen_type"),
                    "screen_details": screen.get("screen_details"),
                    "features": screen.get("features")
                }
                user_prompt = user_template.replace("{{ matrix }}", json.dumps({"name": comp["app_type"].replace("App", " App"), "levels": matrix_section}, ensure_ascii=False)).replace("{{ object }}", json.dumps(obj, ensure_ascii=False))
                llm_response = call_llm(prompt=user_prompt, model="gpt-4-1106-preview", temperature=0.1, system_message=system_message)
                try:
                    cleaned = clean_llm_json(llm_response)
                    result = json.loads(cleaned)
                except Exception:
                    result = {"error": "LLM output not valid JSON", "raw": llm_response}
                results.append(result)
        # PowerAutomate, PowerBI: per component
        elif comp.get("flow_type") == "PowerAutomate":
            matrix_section = get_matrix_section("PowerAutomate")
            obj = comp.copy()
            user_prompt = user_template.replace("{{ matrix }}", json.dumps({"name": "Power Automate", "levels": matrix_section}, ensure_ascii=False)).replace("{{ object }}", json.dumps(obj, ensure_ascii=False))
            llm_response = call_llm(prompt=user_prompt, model="gpt-4-1106-preview", temperature=0.1, system_message=system_message)
            try:
                cleaned = clean_llm_json(llm_response)
                result = json.loads(cleaned)
            except Exception:
                result = {"error": "LLM output not valid JSON", "raw": llm_response}
            results.append(result)
        elif comp.get("app_type") == "PowerBI":
            matrix_section = get_matrix_section("PowerBI")
            for screen in comp.get("app_screens", []):
                obj = {
                    "screen_name": screen.get("screen_name"),
                    "screen_type": screen.get("screen_type"),
                    "screen_details": screen.get("screen_details"),
                    "features": screen.get("features")
                }
                user_prompt = user_template.replace("{{ matrix }}", json.dumps({"name": "Power BI", "levels": matrix_section}, ensure_ascii=False)).replace("{{ object }}", json.dumps(obj, ensure_ascii=False))
                llm_response = call_llm(prompt=user_prompt, model="gpt-4-1106-preview", temperature=0.1, system_message=system_message)
                try:
                    cleaned = clean_llm_json(llm_response)
                    result = json.loads(cleaned)
                except Exception:
                    result = {"error": "LLM output not valid JSON", "raw": llm_response}
                results.append(result)
        elif comp.get("app_type") == "PowerPages":
            matrix_section = get_matrix_section("PowerPages")
            for screen in comp.get("app_screens", []):
                obj = {
                    "screen_name": screen.get("screen_name"),
                    "screen_type": screen.get("screen_type"),
                    "screen_details": screen.get("screen_details"),
                    "features": screen.get("features")
                }
                user_prompt = user_template.replace("{{ matrix }}", json.dumps({"name": "Power Pages", "levels": matrix_section}, ensure_ascii=False)).replace("{{ object }}", json.dumps(obj, ensure_ascii=False))
                llm_response = call_llm(prompt=user_prompt, model="gpt-4-1106-preview", temperature=0.1, system_message=system_message)
                try:
                    cleaned = clean_llm_json(llm_response)
                    result = json.loads(cleaned)
                except Exception:
                    result = {"error": "LLM output not valid JSON", "raw": llm_response}
                results.append(result)
    # Save and update state
    with open(ESTIMATION_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    state.estimation_output = results
    save_to_cache("estimation_agent", results)
    console.print(f"[EstimationAgent] Estimation output written to {ESTIMATION_OUTPUT_PATH}")
    return state
