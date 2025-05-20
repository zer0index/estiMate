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
  - `feature_extractor`: Extracts features for each app screen/flow action using a robust dictionary schema.
- **Robust Caching**: Each node checks for cached output in `memory/` and skips execution if present, saving tokens and time.
- **Reusable LLM Utility**: `graph/llm.py` for configurable OpenAI calls (model, temperature, etc).
- **Pydantic Schemas**: For state, PRD chunks, and strategic context, including features as `Dict[str, str]` for extensibility.
- **Prompt Templates**: YAML-based, e.g., `strategic_overview.yaml`, `feature_extractor.yaml`.
- **Memory Folder**: All node outputs are written to `memory/` as JSON or markdown files.

---

## File Structure

```
graph/
  ├── graph.py                # DAG definition (nodes, edges, state schema)
  ├── llm.py                  # LLM utility for OpenAI calls
  ├── utils.py                # Helpers for chunking, caching, LLM cleaning
  ├── nodes/
  │     ├── prechunker.py
  │     ├── chunker.py
  │     ├── strategic_overview.py
  │     └── feature_extractor.py
  ├── schemas/
  │     ├── state.py
  │     ├── prd_chunk.py
  │     └── strategic_overview.py
  └── prompts/
        ├── strategic_overview.yaml
        └── feature_extractor.yaml
memory/
  ├── prechunker_output.json
  ├── chunker_output.json
  ├── strategic_overview_output.json
  ├── feature_extractor_output.json
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
   - `memory/feature_extractor_output.json`: MVP components with robust feature dictionaries.

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
  - Node outputs are cached in `memory/` as `*_output.json`.
  - To clear all caches, use:
    ```python
    from graph.utils import clear_cache
    clear_cache()  # Clear all caches
    ```
  - Or clear a specific node:
    ```python
    clear_cache("feature_extractor")
    ```

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) 