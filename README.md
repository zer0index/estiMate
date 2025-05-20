# Power Platform Project Estimation Tool (LangGraph)

This project is a modular, multi-agent Power Platform project estimation tool built with [LangGraph](https://langchain-ai.github.io/langgraph/), [Pydantic](https://docs.pydantic.dev/), and [OpenAI](https://platform.openai.com/).

It uses a DAG of agents to process a PRD (Product Requirements Document) and extract structured project context, with robust caching and a modern, extensible feature extraction schema.

---

## Key Features & Structure

- **LangGraph DAG**: Orchestrates nodes/agents with explicit edges and a Pydantic state schema.
- **Nodes/Agents**:
  - `prechunker`: Tags PRD sections for chunking.
  - `chunker`: Splits the tagged PRD into logical chunks.
  - `strategic_overview`: Uses an LLM to extract and validate strategic project context.
  - `canvas_app_agent`, `power_automate_agent`, `database_node`: Specialized extraction and modeling nodes.
- **Robust Caching**: Each node checks for cached output in `memory/` and skips execution if present, saving tokens and time. Each node's cache is stored as `memory/{node}_output.json`.
- **Reusable LLM Utility**: `graph/utils/llm.py` for configurable OpenAI calls (model, temperature, etc) and YAML prompt loading.
- **Pydantic Schemas**: For state, PRD chunks, and strategic context, including features as `Dict[str, str]` for extensibility.
- **Prompt Templates**: YAML-based, e.g., `strategic_overview.yaml`, `database_node.yaml`.
- **Memory Folder**: All node outputs are written to `memory/` as JSON or markdown files.

---

## File Structure

```
graph/
  ├── graph.py                # DAG definition (nodes, edges, state schema)
  ├── utils/
  │     ├── llm.py            # LLM utility for OpenAI calls and YAML prompt loading
  │     ├── cache.py          # Per-node cache utility (get_cache, set_cache)
  │     └── utils.py          # Helpers for chunking, LLM cleaning, etc.
  ├── nodes/
  │     ├── prechunker.py
  │     ├── chunker.py
  │     ├── strategic_overview.py
  │     ├── canvas_app_agent.py
  │     ├── power_automate_agent.py
  │     └── database_node.py
  ├── schemas/
  │     ├── state.py
  │     ├── prd_chunk.py
  │     └── strategic_overview.py
  └── prompts/
        ├── strategic_overview.yaml
        ├── database_node.yaml
        └── ...
memory/
  ├── prechunker_output.json
  ├── chunker_output.json
  ├── strategic_overview_output.json
  ├── canvas_app_agent_output.json
  ├── power_automate_agent_output.json
  ├── database_node_output.json
  └── 1_tagged.md
input/
  └── *.md (your PRD files)
main.py                      # CLI entrypoint
requirements.txt             # Dependencies
.env                         # Your OpenAI API key
```

---

## Setup & Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your OpenAI API key in a `.env` file:**
   ```env
   OPENAI_API_KEY=your-api-key-here
   ```
3. **Prepare your PRD input:**
   - Place one or more PRD markdown files in the `input/` folder.
4. **Run the pipeline:**
   ```bash
   python -m main
   ```
   - You'll be prompted to select a PRD file to process.
5. **Outputs:**
   - `memory/1_tagged.md`: PRD with chunk markers.
   - `memory/prechunker_output.json`: Prechunker completion marker.
   - `memory/chunker_output.json`: List of PRD chunks.
   - `memory/strategic_overview_output.json`: Extracted and validated strategic context.
   - `memory/canvas_app_agent_output.json`: Canvas app features.
   - `memory/power_automate_agent_output.json`: Power Automate actions/connectors.
   - `memory/database_node_output.json`: Proposed normalized database model.

---

## Feature Extraction Schema

Features for each app screen and flow action are now stored as a dictionary with unique keys and descriptive values:

```json
"features": {
  "feat_0001": "Header component",
  "feat_0002": "Device browsing gallery",
  "feat_0003": "Footer component"
}
```
This schema is robust, extensible, and LLM-friendly.

---

## Extending

- **Add new nodes/agents:** Place in `graph/nodes/` and register in `graph/graph.py`.
- **Define new schemas:** In `graph/schemas/`.
- **Add new prompt templates:** In `graph/prompts/`.
- **Use the shared `call_llm` utility** for all LLM-based nodes.
- **Cache management:**
  - Node outputs are cached in `memory/` as `{node}_output.json`.
  - To clear a specific node's cache, delete the corresponding file in `memory/`.

---

## Requirements

- Python 3.9+
- `langgraph`, `pydantic`, `openai`, `python-dotenv`, `PyYAML`

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) 