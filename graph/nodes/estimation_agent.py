"""
Estimation Agent node: Uses LLM and the estimation matrix to estimate effort for each component/screen in the merged output.
"""
import os
import json
from typing import Any
from graph.utils.llm import call_llm
from graph.utils.utils import save_to_cache
from rich.console import Console

console = Console()

MATRIX_PATH = os.path.join("graph", "matrix", "matrix.json")
ESTIMATION_OUTPUT_PATH = os.path.join("memory", "estimation_agent_output.json")

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

# Helper: LLM prompt
LLM_PROMPT = """
You are an expert Power Platform solution estimator. You will be given:
- A matrix describing effort levels for a component type (see 'matrix' below)
- The features/details of a single screen or component (see 'object' below)

Your task:
1. Select the best-matching level from the matrix for this object.
2. Estimate the effort in hours as a range: optimistic, most likely, pessimistic (use the matrix's effort_hours, but adjust if needed).
3. List any assumptions you make (e.g., data provided by customer, security handled externally, etc).
4. Provide reasoning for your scoring and effort estimate.

Respond in this JSON format:
{
  "component_type": string,
  "component_name": string,
  "screen_name": string (if applicable),
  "level_selected": int,
  "score": int,
  "effort_hours": {"optimistic": int, "most_likely": int, "pessimistic": int},
  "assumptions": [string, ...],
  "reasoning": string
}
"""

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
                llm_input = {"matrix": {"name": comp["app_type"].replace("App", " App"), "levels": matrix_section}, "object": obj}
                llm_response = call_llm(prompt=json.dumps(llm_input), model="gpt-4-1106-preview", temperature=0.1, system_message=LLM_PROMPT)
                try:
                    result = json.loads(llm_response)
                except Exception:
                    result = {"error": "LLM output not valid JSON", "raw": llm_response}
                results.append(result)
        # PowerAutomate, PowerBI: per component
        elif comp.get("flow_type") == "PowerAutomate":
            matrix_section = get_matrix_section("PowerAutomate")
            obj = comp.copy()
            llm_input = {"matrix": {"name": "Power Automate", "levels": matrix_section}, "object": obj}
            llm_response = call_llm(prompt=json.dumps(llm_input), model="gpt-4-1106-preview", temperature=0.1, system_message=LLM_PROMPT)
            try:
                result = json.loads(llm_response)
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
                llm_input = {"matrix": {"name": "Power BI", "levels": matrix_section}, "object": obj}
                llm_response = call_llm(prompt=json.dumps(llm_input), model="gpt-4-1106-preview", temperature=0.1, system_message=LLM_PROMPT)
                try:
                    result = json.loads(llm_response)
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
                llm_input = {"matrix": {"name": "Power Pages", "levels": matrix_section}, "object": obj}
                llm_response = call_llm(prompt=json.dumps(llm_input), model="gpt-4-1106-preview", temperature=0.1, system_message=LLM_PROMPT)
                try:
                    result = json.loads(llm_response)
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
