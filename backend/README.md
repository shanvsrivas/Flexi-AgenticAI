# Backend

`studybuddy/` contains the application logic, independent of the Streamlit interface:

| Module | Responsibility |
|---|---|
| `graph.py` | Shared state, nodes, routing, interruptions, and revision loops |
| `agent.py` | Available tool descriptions, model decision context, and action validation |
| `llm.py` | Groq and optional LM Studio connections, tutoring prompts, and structured output |
| `models.py` | Pydantic schemas for generated questions and lessons |
| `tools.py` | Note preparation, lexical retrieval, validation, similarity checks, and scoring |
| `sample.py` | Fixed notes and questions for the labelled sample demo |
| `export.py` | Markdown and JSON evidence exports |

The backend is called by the Streamlit frontend in the same Python process. Inference runs on Groq by default; the optional LM Studio setup uses a separate local model server. No additional backend web server is required.

The default model is GPT-OSS 20B (`openai/gpt-oss-20b`) through Groq. The optional local adapter uses Qwen 2.5 7B Instruct (`qwen2.5-7b-instruct`). Server settings come from Streamlit Secrets or environment variables; see `.streamlit/secrets.toml.example`. No key is entered by students, and no automatic provider fallback is used.

`LocalTutor.decide` selects a tool using schema-constrained JSON. LangGraph executes the chosen action, observes its result, and asks the agent what to do next. `LocalTutor.teach` generates fresh explanations, examples, extra background, and self-check questions. Those additions are distinguished from original source text and are not claimed to be independently fact-checked.

Backend tests live under `tests/backend/`. The root `pytest.ini` makes this source folder importable during tests; `scripts/live_smoke.py` configures the same import path when run directly.
