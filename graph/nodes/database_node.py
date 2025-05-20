from typing import Any, Dict
from pathlib import Path
import json
from pydantic import ValidationError
from graph.schemas.strategic_overview import StrategicContext, DatabaseModel

# You may need to adjust these imports based on your project structure
from graph.utils.llm import call_llm_with_yaml_prompt  # Updated import after moving llm.py
from graph.utils.cache import get_cache, set_cache      # Assumed cache utilities

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "database_node.yaml"
CACHE_KEY = "database_model"


def database_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node to propose a normalized database model based on the project context.
    Updates the state's 'database_model' field with a validated DatabaseModel object.
    """
    # 1. Check for cached output
    cache = get_cache(CACHE_KEY)
    if cache is not None:
        state.database_model = DatabaseModel(**cache)
        print("[DatabaseNode] Loaded database model from cache.")
        return state

    # 2. Prepare context for prompt
    context = getattr(state, "strategic_context", None)
    if not context:
        raise ValueError("Strategic context missing from state.")
    if isinstance(context, dict):
        context = StrategicContext(**context)

    # 3. Render prompt and call LLM
    llm_response = call_llm_with_yaml_prompt(
        prompt_path=str(PROMPT_PATH),
        context=context.dict(),
        model="gpt-4",
        temperature=0.2,
        max_tokens=2048,
    )

    # 4. Parse and validate output
    try:
        db_model_dict = json.loads(llm_response)
        db_model = DatabaseModel(**db_model_dict)
    except (json.JSONDecodeError, ValidationError) as e:
        print("[DatabaseNode] Error parsing LLM output:", e)
        raise

    # 5. Update state and cache
    state.database_model = db_model
    set_cache(CACHE_KEY, db_model.dict())
    print("[DatabaseNode] Database model generated and cached.")
    return state 