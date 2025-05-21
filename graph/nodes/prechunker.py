"""
Prechunker node: Tags PRD for chunking by adding chunk markers.
"""
from graph.utils.utils import add_chunk_markers_and_save, load_from_cache, save_to_cache
from typing import Any
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.markdown import Markdown

console = Console()

def prechunker(state: Any) -> Any:
    """Tags PRD for chunking and returns the updated state."""
    # Use rich for status output
    if console:
        console.print("[bold cyan]Prechunker node: checking cache...[/bold cyan]")
    else:
        print("Prechunker node: checking cache...")
    
    # Try to load from cache first
    cached_data = load_from_cache("prechunker")
    if cached_data is not None and os.path.exists("memory/1_tagged.md"):
        if console:
            console.print("[green][Cache] Prechunker node: using cached output[/green]")
        else:
            print("Prechunker node: using cached output")
        return state

    if console:
        console.print("[yellow]Prechunker node: tagging PRD for chunking...[/yellow]")
    else:
        print("Prechunker node: tagging PRD for chunking...")
    input_path = getattr(state, "input_path", None) or "input/device_order_app_prd.md"
    add_chunk_markers_and_save(input_path)
    
    # Save to cache (just a marker since the actual output is in 1_tagged.md)
    save_to_cache("prechunker", {"completed": True})
    
    if console:
        console.print("[green]Prechunker node: completed and cached.[/green]")
    
    return state