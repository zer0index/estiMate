from typing import Optional, List, Any
from pydantic import BaseModel

class State(BaseModel):
    input_path: Optional[str] = None
    chunks: Optional[List[Any]] = None
    strategic_context: Optional[Any] = None
    component_index: Optional[int] = None  # Used for routing/agent processing
    # Add more fields as needed for your DAG 