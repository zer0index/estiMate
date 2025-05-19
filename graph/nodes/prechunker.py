"""
Prechunker node: Tags PRD for chunking by adding chunk markers.
"""
from graph.utils import add_chunk_markers_and_save
from typing import Any

def prechunker(state: Any) -> Any:
    """Tags PRD for chunking and returns the updated state."""
    print("Prechunker node: tagging PRD for chunking...")
    add_chunk_markers_and_save()
    return state 