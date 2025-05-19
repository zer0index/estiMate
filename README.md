# Power Platform Project Estimation Tool (LangGraph)

This project is a modular, multi-agent Power Platform project estimation tool built with [LangGraph](https://langchain-ai.github.io/langgraph/), [Pydantic](https://docs.pydantic.dev/), and [OpenAI](https://platform.openai.com/).

It uses a DAG of agents to process a PRD (Product Requirements Document) and extract structured project context.

---

## Key Features & Structure

- **LangGraph DAG**: Orchestrates nodes/agents with explicit edges and a Pydantic state schema.
- **Nodes/Agents**:
  - `prechunker`: Tags PRD sections for chunking.
  - `chunker`: Splits the tagged PRD into logical chunks.
  - `strategic_overview`: Uses an LLM to extract and validate strategic project context, saving output to `memory/strategic_context.json`.
- **Reusable LLM Utility**: `graph/llm.py` for configurable OpenAI calls (model, temperature, etc).
- **Pydantic Schemas**: For state, PRD chunks, and strategic context.
- **Prompt Templates**: YAML-based, e.g., `strategic_overview.yaml`.
- **Memory Folder**: All node outputs are written to `memory/`.

---

## File Structure

```
graph/
  ├── graph.py                # DAG definition (nodes, edges, state schema)
  ├── llm.py                  # LLM utility for OpenAI calls
  ├── utils.py                # Helper for chunk marker insertion
  ├── nodes/
  │     ├── prechunker.py
  │     ├── chunker.py
  │     └── strategic_overview.py
  ├── schemas/
  │     ├── state.py
  │     ├── prd_chunk.py
  │     └── strategic_overview.py
  └── prompts/
        └── strategic_overview.yaml
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
   - Place your PRD markdown file at `input/device_order_app_prd.md`.
4. **Run the pipeline:**
   ```bash
   python -m main
   ```
5. **Outputs:**
   - `memory/1_tagged.md`: PRD with chunk markers.
   - `memory/prd_chunks.json`: List of PRD chunks.
   - `memory/strategic_context.json`: Extracted and validated strategic context.

---

## Extending

- Add new nodes/agents in `graph/nodes/` and register them in `graph/graph.py`.
- Define new schemas in `graph/schemas/`.
- Add new prompt templates in `graph/prompts/`.
- Use the shared `call_llm` utility for all LLM-based nodes.

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) 