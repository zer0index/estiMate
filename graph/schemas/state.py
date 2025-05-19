from typing import Optional, List, Any
from pydantic import BaseModel

class State(BaseModel):
    chunks: Optional[List[Any]] = None
    strategic_context: Optional[Any] = None
    # Add more fields as needed for your DAG 