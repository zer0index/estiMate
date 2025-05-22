# extractor_agent.py
"""
Extractor Agent: Generates a project estimation XLSX file with a summary sheet based on outputs in the .memory folder.
"""
import os
import json
from typing import List, Dict, Any
from openpyxl import Workbook

MEMORY_DIR = os.path.join(os.path.dirname(__file__), '../../memory')
OUTPUT_XLSX = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../project_estimation_summary.xlsx'))

# Remove 'Strategic Overview' from component map
COMPONENT_FILE_MAP = {
    'canvas_app_agent_output.json': 'Canvas App',
    'model_driven_agent_output.json': 'Model-Driven App',
    'power_automate_agent_output.json': 'Power Automate',
    'database_model_output.json': 'Database',
    'estimation_agent_output.json': 'Estimation',
}

def load_json(path: str) -> Any:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def extract_summary_data(memory_dir: str) -> List[Dict[str, Any]]:
    summary = []
    files = os.listdir(memory_dir)
    estimation = load_json(os.path.join(memory_dir, 'estimation_agent_output.json'))
    hours_by_component = {}
    if estimation:
        for item in estimation:
            ctype = item.get('component_type', 'Unknown')
            name = item.get('component_name', 'Unknown')
            key = (ctype, name)
            hours = item.get('effort_hours', {})
            if key not in hours_by_component:
                hours_by_component[key] = {'optimistic': 0, 'most_likely': 0, 'pessimistic': 0}
            for k in ['optimistic', 'most_likely', 'pessimistic']:
                hours_by_component[key][k] += hours.get(k, 0)
    for fname in files:
        if fname.endswith('.json') and fname in COMPONENT_FILE_MAP:
            data = load_json(os.path.join(memory_dir, fname))
            ctype = COMPONENT_FILE_MAP[fname]
            if fname == 'estimation_agent_output.json':
                continue  # Already processed
            if isinstance(data, dict):
                # Try to extract name, description, features, assumptions
                mvp = data.get('mvp_components', [{}])[0]
                name = mvp.get('app_name') or mvp.get('flow_name') or data.get('tables', [{}])[0].get('table_name') or 'Unknown'
                desc = mvp.get('app_details') or mvp.get('flow_details') or data.get('tables', [{}])[0].get('description') or data.get('purpose') or ''
                # Safely extract features
                features = ''
                app_screens = mvp.get('app_screens')
                if app_screens and isinstance(app_screens, list) and len(app_screens) > 0:
                    screen_features = app_screens[0].get('features')
                    if isinstance(screen_features, dict):
                        features = ', '.join(screen_features.values())
                assumptions = ''
            elif isinstance(data, list):
                # Fallback for list-based outputs
                name = data[0].get('component_name', 'Unknown')
                desc = data[0].get('reasoning', '')
                features = ''
                assumptions = ', '.join(data[0].get('assumptions', []))
            else:
                continue
            key = (ctype, name)
            hours = hours_by_component.get(key, {'optimistic': 0, 'most_likely': 0, 'pessimistic': 0})
            summary.append({
                'Component Type': ctype,
                'Name': name,
                'Description': desc,
                'Key Features': features,
                'Total Estimated Hours (Opt/ML/Pess)': f"{hours['optimistic']}/{hours['most_likely']}/{hours['pessimistic']}",
                'Assumptions': assumptions,
                'Source File': fname
            })
    return summary

def write_summary_xlsx(summary: List[Dict[str, Any]], output_path: str, metadata: Dict[str, str], totals: Dict[str, int], global_assumptions: str):
    # Ensure the export directory exists
    export_dir = os.path.dirname(output_path)
    os.makedirs(export_dir, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    # Project Metadata (Top Section)
    ws.append(["Project Name", metadata.get("project_name", "")])
    ws.append(["PRD File Used", metadata.get("prd_file", "")])
    ws.append(["Date Generated", metadata.get("date_generated", "")])
    ws.append(["Prepared By", metadata.get("prepared_by", "")])
    ws.append(["Pipeline Run ID", metadata.get("pipeline_run_id", "")])
    ws.append([])

    # High-Level Project Description
    ws.append(["Purpose:", metadata.get("purpose", "")])
    ws.append(["Business Value:", metadata.get("business_value", "")])
    ws.append(["MVP Scope:", metadata.get("mvp_scope", "")])
    ws.append([])

    # Component Overview Table
    headers = [
        'Component Type', 'Name/ID', 'Description', 'Key Features',
        'Optimistic Hours', 'Most Likely Hours', 'Pessimistic Hours', 'Assumptions'
    ]
    ws.append(headers)
    for row in summary:
        ws.append([
            row['Component Type'], row['Name'], row['Description'], row['Key Features'],
            row['Optimistic Hours'], row['Most Likely Hours'], row['Pessimistic Hours'], row['Assumptions']
        ])
    # Totals Row
    ws.append([
        'TOTAL', '', '', '',
        totals['optimistic'], totals['most_likely'], totals['pessimistic'], ''
    ])
    ws.append([])

    # Global Assumptions & Notes
    ws.append(["Global Assumptions & Notes:"])
    ws.append([global_assumptions])
    wb.save(output_path)

def extractor_agent(state):
    # Metadata extraction
    metadata = {
        "project_name": os.path.splitext(os.path.basename(state.input_path))[0] if hasattr(state, 'input_path') else "Project",
        "prd_file": os.path.basename(state.input_path) if hasattr(state, 'input_path') else "",
        "date_generated": "2025-05-22",
        "prepared_by": "estiMate AI Pipeline",
        "pipeline_run_id": getattr(state, 'run_id', ''),
        "purpose": '',
        "business_value": '',
        "mvp_scope": ''
    }
    # Load strategic overview for purpose, business value, mvp scope
    strategic = load_json(os.path.join(MEMORY_DIR, 'strategic_overview_output.json'))
    if strategic:
        metadata["purpose"] = strategic.get("purpose", "")
        metadata["business_value"] = ', '.join(strategic.get("business_value", []))
        mvp = strategic.get("mvp_components", [])
        if mvp:
            metadata["mvp_scope"] = '; '.join([c.get('app_name', c.get('flow_name', '')) for c in mvp if c.get('app_name') or c.get('flow_name')])
    # Extract summary data from estimation_agent_output.json as source of truth
    summary = []
    totals = {'optimistic': 0, 'most_likely': 0, 'pessimistic': 0}
    global_assumptions = []
    estimation = load_json(os.path.join(MEMORY_DIR, 'estimation_agent_output.json'))
    # Build a lookup for details from agent outputs
    details_lookup = {}
    files = os.listdir(MEMORY_DIR)
    for fname in files:
        if fname.endswith('.json') and fname in COMPONENT_FILE_MAP and fname != 'estimation_agent_output.json':
            data = load_json(os.path.join(MEMORY_DIR, fname))
            ctype = COMPONENT_FILE_MAP[fname]
            if isinstance(data, dict):
                mvp = data.get('mvp_components', [{}])[0]
                details_lookup[(ctype, mvp.get('app_name') or mvp.get('flow_name') or data.get('tables', [{}])[0].get('table_name') or 'Unknown')] = {
                    'desc': mvp.get('app_details') or mvp.get('flow_details') or data.get('tables', [{}])[0].get('description') or data.get('purpose') or '',
                    'features': '',
                }
                app_screens = mvp.get('app_screens')
                if app_screens and isinstance(app_screens, list) and len(app_screens) > 0:
                    screen_features = app_screens[0].get('features')
                    if isinstance(screen_features, dict):
                        details_lookup[(ctype, mvp.get('app_name') or mvp.get('flow_name') or data.get('tables', [{}])[0].get('table_name') or 'Unknown')]['features'] = ', '.join(screen_features.values())
    # Aggregate hours and assumptions by component
    component_agg = {}
    if estimation:
        for item in estimation:
            ctype = item.get('component_type', 'Unknown')
            name = item.get('component_name', 'Unknown')
            if ctype == 'Strategic Overview':
                continue  # skip
            key = (ctype, name)
            hours = item.get('effort_hours', {})
            if key not in component_agg:
                component_agg[key] = {
                    'optimistic': 0, 'most_likely': 0, 'pessimistic': 0,
                    'assumptions': set()
                }
            component_agg[key]['optimistic'] += hours.get('optimistic', 0)
            component_agg[key]['most_likely'] += hours.get('most_likely', 0)
            component_agg[key]['pessimistic'] += hours.get('pessimistic', 0)
            for a in item.get('assumptions', []):
                component_agg[key]['assumptions'].add(a)
    # Build summary from aggregated data, skip any Unknowns
    for key, hours in component_agg.items():
        ctype, name = key
        if ctype == 'Unknown' or name == 'Unknown':
            continue  # skip any unknowns
        totals['optimistic'] += hours['optimistic']
        totals['most_likely'] += hours['most_likely']
        totals['pessimistic'] += hours['pessimistic']
        assumptions = ', '.join(hours['assumptions'])
        if hours['assumptions']:
            global_assumptions.extend(list(hours['assumptions']))
        desc = ''
        features = ''
        if key in details_lookup:
            desc = details_lookup[key]['desc']
            features = details_lookup[key]['features']
        summary.append({
            'Component Type': ctype,
            'Name': name,
            'Description': desc,
            'Key Features': features,
            'Optimistic Hours': hours['optimistic'],
            'Most Likely Hours': hours['most_likely'],
            'Pessimistic Hours': hours['pessimistic'],
            'Assumptions': assumptions
        })
    write_summary_xlsx(summary, OUTPUT_XLSX, metadata, totals, '\n'.join(global_assumptions))
    print(f"Project estimation summary written to {OUTPUT_XLSX}")
    return state

if __name__ == '__main__':
    extractor_agent()
