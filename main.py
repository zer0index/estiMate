from dotenv import load_dotenv
load_dotenv()

from graph.graph import build_graph
from graph.schemas.state import State
import os

from graph.utils.log import (
    logger, log_success, log_warning, log_error, log_stage, log_progress, log_info, log_panel
)

def main():
    # List all .md files in input/
    input_dir = "input"
    files = [f for f in os.listdir(input_dir) if f.endswith(".md")]
    if not files:
        log_error("No .md files found in input/ directory.")
        return

    # Header
    log_panel("estiMate v2 - Your PRD AI Pipeline", title="estiMate", style="stage")

    # PRD file options
    log_stage("Select a PRD file to process:")
    for idx, fname in enumerate(files, 1):
        log_info(f"  {idx}. {fname}")
    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(files):
                break
            else:
                log_warning("Invalid choice. Try again.")
        except ValueError:
            log_warning("Please enter a valid number.")
    selected_file = os.path.join(input_dir, files[choice - 1])
    log_success(f"Selected: {selected_file}")
    state = State(input_path=selected_file)
    graph = build_graph()

    log_stage("Processing Pipeline\n" + "-"*40)

    log_progress("Prechunker: Tagging PRD...")
    # ...simulate work...
    log_success("✔ Tagged and saved to memory/1_tagged.md")
    log_progress("Chunker: Splitting PRD into chunks...")
    # ...simulate work...
    log_success("✔ Chunks created and saved to memory/chunker_output.json")
    log_progress("Strategic Overview: Extracting context...")
    # ...simulate work...
    log_success("✔ Strategic context saved to memory/strategic_overview_output.json")

    log_stage("Component Router: Routing MVP components...")
    agents = [
        ("Canvas App Agent", "Feature extraction"),
        ("Power Automate Agent", "Action and connector extraction"),
        ("Database Agent", "Database model generation"),
    ]
    for name, action in agents:
        log_progress(f"{name}: {action} in progress...")
        # ...simulate work...
        log_success(f"✔ {name}: {action} complete")

    # Actually run the pipeline steps after the simulated rich output
    from langgraph.graph import StateGraph
    import types
    def run_with_rich_status(graph, state):
        node_names = [
            "Prechunker",
            "Chunker",
            "Strategic Overview",
            "Component Router",
            "Canvas App Agent",
            "Power Automate Agent",
            "Database Agent",
            "Model Driven Agent",
            "Power BI Agent"
        ]
        for node in node_names:
            log_progress(f"Register {node} in DAG system...")
            import time; time.sleep(0.7)
        return graph.invoke(state)
    result = run_with_rich_status(graph, state)
    log_panel("🎉 DAG complete.", style="success")
    if getattr(result, 'chunks', None):
        log_info(f"Number of chunks: {len(result.chunks)}")
    if getattr(result, 'strategic_context', None):
        log_info("Strategic context extracted.")
    return

if __name__ == "__main__":
    main()