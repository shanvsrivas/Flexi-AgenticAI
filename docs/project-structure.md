# Project structure and submission map

```text
AgenticAI/
├── frontend/
│   ├── app.py                         Streamlit entry point
│   ├── assets/
│   │   └── styles.css                 Visual styling
│   └── README.md
├── backend/
│   ├── studybuddy/
│   │   ├── __init__.py
│   │   ├── graph.py                   LangGraph state and workflow
│   │   ├── agent.py                   Tool catalogue and action rules
│   │   ├── llm.py                     LM Studio model connection
│   │   ├── models.py                  Structured output validation
│   │   ├── tools.py                   Retrieval, checking, and scoring
│   │   ├── sample.py                  Offline demo fixtures
│   │   └── export.py                  Evidence downloads
│   └── README.md
├── tests/
│   ├── backend/test_workflow.py       Core workflow and adapter tests
│   ├── backend/test_agent.py          Model-selected actions and expanded teaching
│   └── frontend/test_app.py           Complete interface journey
├── docs/
│   ├── report-draft.md                Submission report draft
│   ├── demo-and-viva.md               Demonstration and explanation guide
│   ├── testing-evidence.md            Test matrix and interpretation
│   ├── project-structure.md           This guide
│   ├── diagrams/workflow.mmd          Mermaid graph definition
│   ├── certificates/
│   │   ├── ai-agents-and-automation.jpg
│   │   └── agentic-ai-with-langgraph.jpg
│   └── requirements/
│       ├── submission-form.jpg
│       └── marking-rubric.jpg
├── artifacts/
│   ├── test-results/                 Automated test reports in XML
│   ├── live-verification/            Actual local-model test output
│   └── screenshots/                  Saved interface screenshots
├── examples/ai-and-langgraph-notes.txt
├── scripts/live_smoke.py             Real-model verification command
├── .streamlit/config.toml            Shared theme and local server settings
├── .gitignore
├── requirements.txt                  Application dependencies
├── requirements-dev.txt              Test dependencies
├── pytest.ini                        Test discovery and backend import path
├── run.ps1                           One-command application launcher
├── setup.ps1                         Dependency setup helper
└── README.md                         Project overview and instructions
```

The local `.venv` and generated Python cache folders are runtime files, so they are omitted from this tree and ignored by Git.

## Where to find each submission requirement

| Requirement / marking criterion | Project location |
|---|---|
| Understanding of agentic AI | `docs/report-draft.md`, section 2 |
| Courses and completion evidence | Report section 3 and `docs/certificates/` |
| Problem statement | Report section 4 |
| Proposed solution | Report section 5 |
| Agent workflow and justified roles | Report section 5, `backend/studybuddy/graph.py`, and `docs/diagrams/workflow.mmd` |
| Implementation and technologies | Report section 6, `frontend/`, and `backend/` |
| Testing outputs and interpretation | `tests/`, `docs/testing-evidence.md`, and `artifacts/` |
| Individual reflection | Report section 9 contains prompts to personalise |
| Demonstration | `docs/demo-and-viva.md` and the running application |
| Conclusion and limitations | Report section 10 |
| Application and GitHub links | Report section 8; final hosting/repository links will be added at the publishing stage |

The supplied screenshots are reference material and completion evidence. The duplicate submission-form screenshot was stored once. Their instructions do not change application behaviour.

## How the layers connect

The Streamlit frontend calls backend functions directly. The backend runs the LangGraph workflow and sends inference requests to LM Studio. The folder separation makes these responsibilities easier to inspect and explain without adding a second application server.

Run everything from `AgenticAI` with `run.ps1`. Run all tests from the same folder:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/test-results/test-results.xml
```
