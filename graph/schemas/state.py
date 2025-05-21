from typing import Optional, List, Any
from pydantic import BaseModel
from graph.schemas.strategic_overview import DatabaseModel

class State(BaseModel):
    input_path: Optional[str] = None
    chunks: Optional[List[Any]] = None
    strategic_context: Optional[Any] = None
    component_index: Optional[int] = None  # Used for routing/agent processing
    database_model: Optional[DatabaseModel] = None  # Added for database node output
    estimation_output: Optional[Any] = None  # Added for estimation_agent output
    merged_output: Optional[Any] = None  # Added for merge_agent output
    # Add more fields as needed for your DAG