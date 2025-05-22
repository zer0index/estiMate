import os
import json
from typing import Any, Optional
from pathlib import Path
import re
from graph.utils.log import log_error, log_success, log_warning, log_info

def add_chunk_markers_and_save(input_path="input/device_order_app_prd.md"):
    """Reads the PRD, inserts chunk markers before each H2 heading, and writes to memory/1_tagged.md."""
    output_path = "memory/1_tagged.md"
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        log_error(f"Input file not found: {input_path}")
        return
    output_lines = []
    chunk_count = 1
    for line in lines:
        if line.strip().startswith("## "):
            output_lines.append(f"<!-- CHUNK_H2_{chunk_count} -->\n")
            chunk_count += 1
        output_lines.append(line)
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(output_lines)
    log_success(f"[Prechunker] Tagged PRD written to {output_path} with {chunk_count-1} chunk markers.")

def get_cache_path(node_name: str) -> str:
    """Returns the cache file path for a given node."""
    return f"memory/{node_name}_output.json"

def save_to_cache(node_name: str, data: Any) -> None:
    """Saves node output to cache file."""
    try:
        from rich.console import Console
        console = Console()
    except ImportError:
        console = None
    cache_path = get_cache_path(node_name)
    try:
        # Convert Pydantic models to dict if needed
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        msg = f"[Cache] Saved output for node '{node_name}' to {cache_path}"
        if console:
            console.print(f"[green]{msg}[/green]")
        else:
            log_success(msg)
    except Exception as e:
        err = f"[Error] Failed to cache output for node '{node_name}': {e}"
        if console:
            console.print(f"[red]{err}[/red]")
        else:
            log_error(err)

def load_from_cache(node_name: str) -> Optional[Any]:
    """Loads node output from cache file if it exists."""
    cache_path = get_cache_path(node_name)
    try:
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            log_info(f"[Cache] Loaded cached output for node '{node_name}' from {cache_path}")
            return data
        return None
    except Exception as e:
        log_error(f"Failed to load cache for node '{node_name}': {e}")
        return None

def clear_cache(node_name: Optional[str] = None) -> None:
    """Clears cache for a specific node or all nodes."""
    try:
        from rich.console import Console
        console = Console()
    except ImportError:
        console = None
    if node_name:
        cache_path = get_cache_path(node_name)
        if os.path.exists(cache_path):
            os.remove(cache_path)
            msg = f"[Cache] Cleared cache for node '{node_name}'"
            if console:
                console.print(f"[yellow]{msg}[/yellow]")
            else:
                log_warning(msg)
    else:
        cache_files = Path("memory").glob("*_output.json")
        for cache_file in cache_files:
            os.remove(cache_file)
        msg = "[Cache] Cleared all node caches"
        if console:
            console.print(f"[yellow]{msg}[/yellow]")
        else:
            log_warning(msg)

def clean_llm_json(text: str) -> str:
    """Clean LLM JSON output: remove code fences, comments, and trailing commas."""
    text = re.sub(r'```(?:json)?', '', text)
    text = re.sub(r'//.*', '', text)
    text = re.sub(r',([ \t\r\n]*[}\]])', r'\1', text)
    return text.strip()