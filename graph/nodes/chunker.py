"""
Chunker node: Splits tagged PRD into chunks and saves as JSON.
"""
import json
import re
from typing import Any
from graph.schemas.prd_chunk import PRDChunk, PRDChunkList
from graph.utils import save_to_cache, load_from_cache

def extract_title(heading_line: str) -> str:
    """Extracts the title from a heading line."""
    match = re.search(r"\*\*(.*?)\*\*", heading_line)
    if match:
        return match.group(1).strip()
    return re.sub(r"^#+\s*\d*\.?\s*", "", heading_line).strip()

def chunker(state: Any) -> Any:
    """Splits tagged PRD into chunks and updates the state."""
    print("Chunker node: checking cache...")
    
    # Try to load from cache first
    cached_data = load_from_cache("chunker")
    if cached_data is not None:
        print("Chunker node: using cached output")
        # Convert dict back to PRDChunk objects
        chunks = [PRDChunk(**chunk) for chunk in cached_data]
        state.chunks = chunks
        return state

    print("Chunker node: splitting tagged PRD into chunks...")
    chunks = []
    current_chunk = []
    current_heading = None
    current_title = None
    order = 1
    in_chunk = False
    with open("memory/1_tagged.md", encoding="utf-8") as f:
        for line in f:
            if line.startswith("<!-- CHUNK_H2_"):
                if in_chunk and current_chunk and current_title:
                    chunks.append(PRDChunk(
                        id=f"H2_{order}_{current_title.replace(' ', '_')}",
                        title=current_title,
                        content="\n".join(current_chunk).strip(),
                        order=order,
                        type="section",
                        raw_heading=current_heading
                    ))
                    order += 1
                    current_chunk = []
                current_heading = line.rstrip()
                current_title = None
                in_chunk = True
                continue
            if in_chunk and current_title is None and line.strip().startswith("##"):
                current_title = extract_title(line.strip())
                continue
            if in_chunk:
                current_chunk.append(line.rstrip())
        if in_chunk and current_chunk and current_title:
            chunks.append(PRDChunk(
                id=f"H2_{order}_{current_title.replace(' ', '_')}",
                title=current_title,
                content="\n".join(current_chunk).strip(),
                order=order,
                type="section",
                raw_heading=current_heading
            ))
    
    state.chunks = chunks
    
    # Save to cache
    save_to_cache("chunker", [chunk.model_dump() for chunk in chunks])
    
    print(f"Chunker node: created {len(chunks)} chunks and saved to cache.")
    return state 