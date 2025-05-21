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
from rich.progress import Progress, SpinnerColumn, TextColumn
from graph.utils.log import log_info, log_success

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
    # Spinner for estimation process
    with Progress(
        SpinnerColumn(style="progress"),
        TextColumn("[progress]Estimating effort for all components...[/progress]"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("estimation", total=None)
        # Check for cached output
        if os.path.exists(ESTIMATION_OUTPUT_PATH):
            log_success(f"[Cache] Using cached output for node 'estimation_agent' at {ESTIMATION_OUTPUT_PATH}")
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
        # Database Model estimation (if present)
        database_model = merged.get("database_model")
        if database_model:
            matrix_section = get_matrix_section("DatabaseModel")
            obj = database_model
            # Compose a prompt for the LLM to estimate the whole database, including table/field/type summary
            system_message, user_template = load_estimation_prompt()
            # Add a summary of tables/fields/types for the LLM
            table_summaries = []
            all_fields = []
            for table in obj.get("tables", []):
                fields = table.get("fields", [])
                field_summaries = [f"{f['name']} ({f['type']})" for f in fields]
                table_summaries.append(f"- {table['table_name']}: " + ", ".join(field_summaries))
                for f in fields:
                    field_obj = {
                        "name": f.get("name"),
                        "type": f.get("type"),
                        "description": f.get("description", ""),
                        "constraints": []
                    }
                    # Try to infer constraints from table definition
                    if table.get("primary_key") == f.get("name"):
                        field_obj["constraints"].append("PRIMARY KEY")
                    if f.get("type", "").lower() in ["int", "integer"]:
                        field_obj["constraints"].append("NOT NULL")
                    # Add foreign key info
                    if table.get("foreign_keys") and f.get("name") in table.get("foreign_keys"):
                        field_obj["constraints"].append(f"FOREIGN KEY REFERENCES {table['table_name']}({f['name']})")
                    all_fields.append(field_obj)
            obj["table_summary"] = "\n".join(table_summaries)
            # Compose a single output object as in the user's example
            db_output = {
                "component_type": "DatabaseModel",
                "component_name": obj.get("notes", "Database Model"),
                "screen_name": None,
                "level_selected": None,  # Will be filled by LLM
                "score": None,           # Will be filled by LLM
                "effort_hours": None,    # Will be filled by LLM
                "table_name": obj.get("notes", "Database Model"),
                "description": obj.get("notes", ""),
                "fields": all_fields,
                "assumptions": [],       # Will be filled by LLM
                "reasoning": ""         # Will be filled by LLM
            }
            # Pass this object to the LLM for estimation
            db_prompt = user_template.replace(
                "{{ matrix }}", json.dumps({"name": "DatabaseModel", "levels": matrix_section}, ensure_ascii=False)
            ).replace(
                "{{ object }}", json.dumps(db_output, ensure_ascii=False)
            )
            llm_response = call_llm(
                prompt=db_prompt,
                model="gpt-4-1106-preview",
                temperature=0.1,
                system_message=system_message
            )
            try:
                cleaned = clean_llm_json(llm_response)
                db_estimate = json.loads(cleaned)
            except Exception:
                db_estimate = {"error": "LLM output not valid JSON", "raw": llm_response}
            results.append(db_estimate)
        # Save and update state
        with open(ESTIMATION_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        state.estimation_output = results
        save_to_cache("estimation_agent", results)
        log_success(f"[EstimationAgent] Estimation output written to {ESTIMATION_OUTPUT_PATH}")
    return state
