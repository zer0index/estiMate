"""
Prechunker node: Tags PRD for chunking by adding chunk markers.
"""
from graph.utils import add_chunk_markers_and_save
from typing import Any

def prechunker(state: Any) -> Any:
    """Tags PRD for chunking and returns the updated state."""
    print("Prechunker node: tagging PRD for chunking...")
    input_path = getattr(state, "input_path", None) or "input/device_order_app_prd.md"
    add_chunk_markers_and_save(input_path)
    return state 