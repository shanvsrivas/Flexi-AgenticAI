# Backend

`studybuddy/` contains the application logic, independent of the Streamlit interface:

| Module | Responsibility |
|---|---|
| `graph.py` | Shared state, nodes, routing, interruptions, and revision loops |
| `agent.py` | Available tool descriptions, model decision context, and action validation |
| `llm.py` | LM Studio connection, generation prompt, structured output, and source lookup |
| `models.py` | Pydantic schemas for generated questions and lessons |
| `tools.py` | Note preparation, lexical retrieval, validation, similarity checks, and scoring |
| `sample.py` | Fixed notes and questions for the labelled sample demo |
| `export.py` | Markdown and JSON evidence exports |

The backend is called by the Streamlit frontend in the same Python process. LM Studio remains a separate local inference server. No additional backend web server is required.

The inference model is fixed to Qwen 2.5 7B Instruct (`qwen2.5-7b-instruct`). Endpoint, optional access token, and timeout come from the server environment; see `.env.example`. Deployment will use the same model with a server-configured inference endpoint.

`LocalTutor.decide` selects a tool using schema-constrained JSON. LangGraph executes the chosen action, observes its result, and asks the agent what to do next. `LocalTutor.teach` generates fresh explanations, examples, extra background, and self-check questions. Those additions are distinguished from original source text and are not claimed to be independently fact-checked.

Backend tests live under `tests/backend/`. The root `pytest.ini` makes this source folder importable during tests; `scripts/live_smoke.py` configures the same import path when run directly.
