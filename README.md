<h1 align="center">🧠 estiMate</h1>
<h3 align="center">An Intelligent, Modular Estimation Pipeline for Power Platform Projects</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue" />
  <img src="https://img.shields.io/badge/Powered_by-OpenAI-yellow" />
  <img src="https://img.shields.io/badge/Framework-LangGraph-purple" />
  <img src="https://img.shields.io/badge/CLI-rich%20output-blueviolet" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 📌 Overview

**estiMate** intelligently breaks down Power Platform project documentation using LLM-powered agents and LangGraph's orchestration system. Each component is processed by a specialized agent, ensuring fast, structured estimates—visualized in a live CLI.

---

## 📚 Table of Contents

- [🚦 Pipeline Overview](#-pipeline-overview)
- [📁 Project Structure](#-project-structure)
- [✨ Core Features](#-core-features)
- [🚀 Getting Started](#-getting-started)
- [💾 Caching System](#-caching-system)
- [🎨 CLI Output](#-cli-output)
- [📊 Excel Export (Summary Sheet)](#-excel-export-summary-sheet)
- [🛠️ Extending estiMate](#️-extending-estimate)
- [📚 Tech Stack](#-tech-stack)
- [🎥 Demo](#-demo)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

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
       (route) ───► database_node      │
        ↓                              │
       (route) ───► model_driven_agent │
        ↓                              │
       (route) ───► powerbi_agent ─────┘
        ↓                              │
       (route) ───► power_pages_agent  │
                                      ↓
                                 merge_agent
                                      ↓
                                 estimation_agent
                                      ↓
                                 extractoin_agent
                                      ↓                                      
                                     END
```

- Built with `StateGraph` from LangGraph
- Routes data dynamically to specialized agents (Canvas App, Power Automate, Database, Model Driven, Power BI, Power Pages)
- All agent outputs are merged by `merge_agent` before estimation
- `merge_agent` ensures all features, actions, connectors, and top-level fields from each agent are included in the final output
- `estimation_agent` produces the final effort/cost estimate
- Automatically loops until all data is processed

---

## 📁 Project Structure

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
│   ├── database_node.py
│   ├── power_pages_agent.py
│   ├── merge_agent.py
│   └── estimation_agent.py
├── schemas/
│   └── state.py
├── prompts/
│   └── *.yaml              # LLM prompt templates
└── utils/
    ├── llm.py
    └── cache.py
```

---

## ✨ Core Features

- 🧱 **Modular architecture** – Each node handles one responsibility
- 🔁 **LLM routing logic** – Chooses the right agent per component
- 💾 **Smart caching** – Skip nodes already processed
- 🧠 **Prompt-driven** – Easily editable YAML-based prompts for all agents, including Power Pages
- 🔒 **Typed state flow** – Pydantic enforces schema integrity
- 🎨 **Rich CLI** – Styled logs, spinners, color-coded output

---

## 🚀 Getting Started

### 1. Clone and install:

```bash
git clone https://github.com/your-org/estimate.git
cd estimate
pip install -r requirements.txt
```

### 2. Run the pipeline:

```bash
python -m main
```

- Select your PRD from `/input`
- Watch each node in action
- Outputs are saved in `/memory/*.json`

---

## 💾 Caching System

Each node writes its result to:

```bash
/memory/{node}_output.json
```

If this file exists, the node is skipped.  
To re-run: delete the corresponding file.

---

## 🎨 CLI Output

- The pipeline provides real-time, colorized feedback in the terminal.
- Each step uses spinners and color-coded status messages for progress, success, and errors.
- If the spinner-based logger is missing, some nodes may fall back to plain or `rich`-styled output.

---

## 📊 Excel Export (Summary Sheet)

After each pipeline run, estiMate generates a comprehensive Excel summary (`project_estimation_summary.xlsx`) in the project root. This file includes:

- **Project Metadata:** Project name, PRD file, date, author, and pipeline run ID
- **High-Level Description:** Purpose, business value, MVP scope
- **Component Overview Table:**
  - Component Type (e.g., Canvas App, Power Automate, Database, etc.)
  - Name/ID
  - Description
  - Key Features
  - Optimistic Hours
  - Most Likely Hours
  - Pessimistic Hours
  - Assumptions
- **Totals Row:** Sums for all hour columns
- **Global Assumptions & Notes:** All collected assumptions and important notes

The summary table is automatically deduplicated and aggregated by component, ensuring each component appears only once with summed hours. No 'Unknown' or 'Strategic Overview' entries are included.

---

## 🛠️ Extending estiMate

Want to add a new component handler?

1. Add a new module under `graph/nodes/`
2. Register the node in `graph.py`
3. Add or update the schema in `graph/schemas/`
4. Write a new YAML prompt in `graph/prompts/`

**For consistent CLI output:**
- Use a logger pattern in your node:
  ```python
  def my_node(state, logger):
      logger.start("Processing...")
      # ...work...
      logger.success("Done!")
      return state
  ```
- If the logger is not available, fallback to `print` or `rich.console` output.

Follow the modular pattern and you're good to go!

---

## 📚 Tech Stack

- 🐍 Python 3.9+
- 🧠 [LangGraph](https://langchain-ai.github.io/langgraph/)
- 🤖 [OpenAI API](https://platform.openai.com/docs)
- 🧬 [Pydantic](https://docs.pydantic.dev/)
- 📜 [PyYAML](https://pyyaml.org/)
- 🎨 [rich](https://github.com/Textualize/rich)

---

## 🎥 Demo

To run the Rich CLI demo:

```bash
python -m main
```

Watch the pipeline animate node-by-node with live, colorized feedback and structured logging.

---

## 🤝 Contributing

We welcome PRs!  
To contribute:

1. Fork the repo
2. Create a feature branch
3. Add your feature with tests
4. Submit a PR

---

## 📄 License

Licensed under the MIT License.  
© Avanade

---

## 🧩 Detailed Project Architecture

estiMatev2 is an intelligent, modular estimation pipeline for Power Platform projects. It processes Product Requirements Documents (PRDs) in Markdown format, breaking them down into structured, actionable components using LLM-powered agents. The pipeline is orchestrated as a Directed Acyclic Graph (DAG) using LangGraph, with each node handling a specific responsibility.

### Main Components

- **main.py**: Entry point. Loads PRD files from `input/`, lets the user select one, and runs the pipeline with rich CLI feedback.
- **graph/graph.py**: Defines the DAG using LangGraph's `StateGraph`. Registers nodes for each processing step and their transitions.
- **graph/nodes/**: Contains modular agent nodes:
  - `prechunker.py`: Tags PRD for chunking.
  - `chunker.py`: Splits PRD into logical chunks.
  - `strategic_overview.py`: Extracts strategic context and high-level architecture.
  - `component_router.py`: Routes each MVP component to the correct agent.
  - `canvas_app_agent.py`, `model_driven_agent.py`, `power_automate_agent.py`, `powerbi_agent.py`, `power_pages_agent.py`: Specialized agents for extracting features from different Power Platform components (including Power Pages).
  - `merge_agent.py`: Merges all agent outputs into a single, well-structured JSON for estimation. Ensures all features, actions, connectors, and top-level fields are included.
  - `estimation_agent.py`: Produces the final effort/cost estimate based on the merged output.
  - `database_node.py`: Proposes a normalized database model.
- **graph/schemas/**: Pydantic models for state, strategic context, components, database, roles, etc. Enforces type safety and structure.
- **graph/prompts/**: YAML prompt templates for each agent, defining system/user instructions for the LLM.
- **graph/utils/**: Utility functions for LLM calls, caching, chunking, and cleaning LLM output.
- **input/**: Contains example PRD markdown files for different use cases.
- **memory/**: Stores intermediate and final outputs (e.g., cached JSON results for each node).

### Pipeline Steps

1. **Prechunker**: Tags PRD sections for chunking.
2. **Chunker**: Splits PRD into manageable chunks.
3. **Strategic Overview**: Extracts project purpose, business value, MVP components, post-MVP modules, roles, constraints, and integration points.
4. **Component Router**: Iterates over MVP components, routing each to the appropriate agent.
5. **Specialized Agents**: Extract features, actions, connectors, screens, etc., for each component type (Canvas App, Model-Driven App, Power Automate, Power BI, Power Pages).
6. **Merge Agent**: Merges all agent outputs into a single, well-structured JSON for estimation. Ensures all features, actions, connectors, and top-level fields are included.
7. **Estimation Agent**: Produces the final effort/cost estimate based on the merged output.
8. **Database Node**: Proposes a normalized database schema based on the extracted context.
9. **Caching**: Each node caches its output in `/memory` to avoid redundant computation.

### Design Principles

- Modular, stateless nodes (functions) with clear input/output.
- Typed state flow using Pydantic models.
- Prompt-driven LLM logic (YAML templates).
- Rich CLI output for user feedback.
- Easily extensible: add new nodes, schemas, and prompts as needed.

- (NEW) **Power Pages Agent**: Specialized agent for extracting features from Power Pages (portal) components, including forms, authentication, web roles, document upload, integrations, and compliance. Prompt-driven and screen-level extraction, similar to Canvas App and Model-Driven agents.

---

<p align="center">
  Made with ❤️
</p>