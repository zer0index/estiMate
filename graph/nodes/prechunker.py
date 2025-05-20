"""
Prechunker node: Tags PRD for chunking by adding chunk markers.
"""
from graph.utils import add_chunk_markers_and_save, load_from_cache, save_to_cache
from typing import Any
import os

def prechunker(state: Any) -> Any:
    """Tags PRD for chunking and returns the updated state."""
    print("Prechunker node: checking cache...")
    
    # Try to load from cache first
    cached_data = load_from_cache("prechunker")
    if cached_data is not None and os.path.exists("memory/1_tagged.md"):
        print("Prechunker node: using cached output")
        return state

    print("Prechunker node: tagging PRD for chunking...")
    input_path = getattr(state, "input_path", None) or "input/device_order_app_prd.md"
    add_chunk_markers_and_save(input_path)
    
    # Save to cache (just a marker since the actual output is in 1_tagged.md)
    save_to_cache("prechunker", {"completed": True})
    
    return state 