from pydantic import BaseModel, Field
from typing import List, Optional

class PRDChunk(BaseModel):
    id: str
    title: str
    content: str
    order: int
    type: str = Field(default="section")
    raw_heading: Optional[str] = None

class PRDChunkList(BaseModel):
    chunks: List[PRDChunk] 