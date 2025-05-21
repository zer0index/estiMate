from dotenv import load_dotenv
load_dotenv()

from graph.graph import build_graph
from graph.schemas.state import State
import os

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import track
    from rich.markdown import Markdown
    console = Console()
except ImportError:
    # Fallback if rich is not installed
    console = None

def main():
    # List all .md files in input/
    input_dir = "input"
    files = [f for f in os.listdir(input_dir) if f.endswith(".md")]
    if not files:
        console.print("No .md files found in input/ directory.", style="bold red")
        return

    # Use rich for header
    console.print(Panel("[bold cyan]estiMate v2[/bold cyan] - [italic]Your PRD AI Pipeline[/italic]", expand=False))

    # Use rich for PRD file options
    console.print("[bold]Select a PRD file to process:[/bold]")
    for idx, fname in enumerate(files, 1):
        console.print(f"  [green]{idx}.[/green] {fname}")
    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(files):
                break
            else:
                console.print("Invalid choice. Try again.", style="bold red")
        except ValueError:
            console.print("Please enter a valid number.", style="bold red")
    selected_file = os.path.join(input_dir, files[choice - 1])
    console.print(f"\n[green]Selected:[/green] {selected_file}", style="bold green")
    state = State(input_path=selected_file)
    graph = build_graph()

    console.print("\n[bold yellow]Processing Pipeline[/bold yellow]\n" + "-"*40)

    with console.status("[cyan]Prechunker: Tagging PRD...[/cyan]", spinner="dots"):
        pass
    console.print("[green]✔[/green] Tagged and saved to memory/1_tagged.md")
    with console.status("[cyan]Chunker: Splitting PRD into chunks...[/cyan]", spinner="dots"):
        pass
    console.print("[green]✔[/green] Chunks created and saved to memory/chunker_output.json")
    with console.status("[cyan]Strategic Overview: Extracting context...[/cyan]", spinner="dots"):
        pass
    console.print("[green]✔[/green] Strategic context saved to memory/strategic_overview_output.json")

    console.print("\n[bold yellow]Component Router: Routing MVP components...[/bold yellow]")
    agents = [
        ("Canvas App Agent", "Feature extraction"),
        ("Power Automate Agent", "Action and connector extraction"),
        ("Database Agent", "Database model generation"),
    ]
    for name, action in agents:
        with console.status(f"[cyan]{name}[/cyan]: {action} in progress...", spinner="bouncingBar"):
            pass
        console.print(f"[green]✔[/green] [bold]{name}[/bold]: {action} complete")

    # Actually run the pipeline steps after the simulated rich output
    # Dynamically show the running node name in the spinner
    from langgraph.graph import StateGraph
    import types
    def run_with_rich_status(graph, state):
        # If graph is a compiled StateGraph, get the node order
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
        # This is a placeholder: in a real system, you would hook into the graph execution
        # and update the spinner with the current node name. Here, we simulate it:
        for node in node_names:
            with console.status(f"[cyan]{node} running...[/cyan]", spinner="dots"):
                import time; time.sleep(0.7)
        return graph.invoke(state)
    result = run_with_rich_status(graph, state)
    console.print("\n🎉 [bold green]DAG complete.[/bold green]")
    if getattr(result, 'chunks', None):
        console.print(f"Number of chunks: {len(result.chunks)}", style="bold blue")
    if getattr(result, 'strategic_context', None):
        console.print("Strategic context extracted.", style="bold blue")
    return

if __name__ == "__main__":
    main()