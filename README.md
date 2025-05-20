# 🧠 estiMate – Power Platform Project Estimation Tool

A modular, intelligent estimation pipeline for Power Platform projects using LangGraph + OpenAI.

---

## 🚦 Pipeline Overview

```
START
  ↓
prechunker
  ↓
chunker
  ↓
strategic_overview
  ↓
component_router ──► canvas_app_agent ─┐
        ↓                              │
       (route) ───► power_automate_agent
        ↓                              │
       (route) ───► database_node ─────┘
                                      ↓
                                     END
```

### 🧠 LangGraph Summary

- Uses `StateGraph` from `langgraph`
- Conditional routing via `component_router`:
  - Dynamically dispatches components to the correct agent
- Agents are looped until all components are handled

---

## 📁 File & Agent Structure

```
graph/
├── graph.py                # DAG definition
├── nodes/
│   ├── prechunker.py
│   ├── chunker.py
│   ├── strategic_overview.py
│   ├── component_router.py
│   ├── canvas_app_agent.py
│   ├── power_automate_agent.py
│   └── database_node.py
├── schemas/
│   ├── state.py            # Full pipeline state model
├── prompts/                # YAML prompt templates
│   └── ...
└── utils/
    ├── llm.py              # OpenAI integration
    └── cache.py            # Per-node caching
```

---

## 📦 Core Features

- 🧱 **Modular agents**, each responsible for one task
- ⚙️ **Conditional routing** based on `component_router` LLM output
- 💾 **Auto-caching** of node outputs in `/memory/`
- 🧠 **LLM-backed prompts** in YAML, editable and reusable
- 🧬 **Pydantic-based schemas** for robust state passing

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
python -m main
```

- Select your PRD file (from `/input`)
- Watch the graph process your document step-by-step
- Outputs saved in `/memory/*.json`

---

## 🔄 Caching

Each node checks `/memory/{node}_output.json` and skips execution if already processed.  
Remove files manually to re-run specific nodes.

---

## 🛠 Extending

- Add new node → `graph/nodes/`
- Register in `graph.py`
- Add schema (if needed) → `graph/schemas/`
- Add YAML prompt → `graph/prompts/`

---

## 📚 Stack

- Python 3.9+
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [OpenAI API](https://platform.openai.com/docs)
- [Pydantic](https://docs.pydantic.dev/)
- [PyYAML](https://pyyaml.org/)
- [rich](https://github.com/Textualize/rich)

---

Made with ❤️ by Avanade AI Innovation