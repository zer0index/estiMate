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

**estiMate** intelligently breaks down Power Platform project documentation using LLM-powered agents and LangGraph’s orchestration system. Each component is processed by a specialized agent, ensuring fast, structured estimates—visualized in a live CLI.

---

## 📚 Table of Contents

- [🚦 Pipeline Overview](#-pipeline-overview)
- [📁 Project Structure](#-project-structure)
- [✨ Core Features](#-core-features)
- [🚀 Getting Started](#-getting-started)
- [💾 Caching System](#-caching-system)
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
       (route) ───► database_node ─────┘
                                      ↓
                                     END
```

- Built with `StateGraph` from LangGraph
- Routes data dynamically to specialized agents
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
│   └── database_node.py
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
- 🧠 **Prompt-driven** – Easily editable YAML-based prompts
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

## 🛠️ Extending estiMate

Want to add a new component handler?

1. Add a new module under `graph/nodes/`
2. Register the node in `graph.py`
3. Add or update the schema in `graph/schemas/`
4. Write a new YAML prompt in `graph/prompts/`

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

<p align="center">
  Made with ❤️
</p>