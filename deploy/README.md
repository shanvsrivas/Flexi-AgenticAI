# Free demonstration deployment

Use **Streamlit Community Cloud** for the website and **Groq's Free plan** for
the model. The deployed tutor uses **GPT-OSS 20B** (`openai/gpt-oss-20b`), which
supports strict JSON Schema responses. LM Studio and a running laptop are not
needed. The LangGraph agent, tools, scoring, and study interface stay the same.

## Account setup

1. Create a free account at [Groq Console](https://console.groq.com) and create
   an API key. Stay on the Free plan; a paid Developer upgrade is not needed.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io) using
   the repository owner's GitHub account, **shanvsrivas**.
3. Keep the API key in the hosting secrets settings. Never put it in source
   code, a report, a screenshot, or a Git commit.

## Publish the application

In Community Cloud, select **Create app**, then use:

| Setting | Value |
| --- | --- |
| Repository | `shanvsrivas/Flexi-AgenticAI` |
| Branch | `main` |
| Entrypoint | `frontend/app.py` |
| Python version in Advanced settings | `3.12` |

In **Advanced settings → Secrets**, enter:

```toml
STUDYBUDDY_PROVIDER = "groq"
GROQ_API_KEY = "your-private-groq-key"
```

Save and deploy. Community Cloud installs the root `requirements.txt` and
provides an HTTPS `streamlit.app` link. Visitors use that link without an API
key or a GitHub account when the app is public. All visitors share the hosting
account's free allowance.

## Verify before sharing

For a local real-inference preflight, copy the example secrets file to
`.streamlit/secrets.toml`, enter the key privately, and run:

```powershell
.\.venv\Scripts\python.exe scripts/check_model.py
```

This checks model discovery and makes a real structured-output request without
printing the key. Automated tests use mocks and are not proof of live inference.

Then use the public website to:

1. Start **My notes** with the supplied example notes and three questions.
2. Submit answers including a mistake and check the extra concept explanation.
3. Try a follow-up quiz if offered, then download the study summary.
4. Open the link from another device or private browser to confirm a separate
   session works.

Only after a live public lesson works should the URL fill the prototype-link
field in the report. Example session uses fixed content and does not test Groq.

## Limits and keeping it accessible

There is no GPU server rental. Groq's Free plan caps requests and tokens, so
this setup suits a small class demo. Several model calls are needed for each
study session. Per-minute limits may require waiting; daily limits may require
returning later. No automatic paid upgrade or alternative-model fallback is
implemented. Check the account's Limits page for its current allowance.
The client retries a short provider rate limit at most twice, with a small
refill margin and at most 65 seconds of total waiting per request. Longer waits
and exhausted limits show a clear message. **Try tutor again** retries the saved
session after a limit clears, keeping submitted answers and existing scores.

Community Cloud may put an inactive app to sleep. Opening the public link can
wake it again. Keep the hosting account, GitHub repository, and Groq key active
for the required days. Free services do not promise uninterrupted availability.
Study progress is held in memory and is lost when the application restarts;
download completed summaries. Live notes and answers are processed by Groq.

## Optional Docker or local Qwen

The Dockerfile is an alternative to Community Cloud, not a requirement. Build
with `docker build -t studybuddy:cloud .`. Set `GROQ_API_KEY` and optionally
`STUDYBUDDY_PROVIDER=groq` in the runtime environment. The app listens on port
8501 and has health path `/_stcore/health`; its proxy must support WebSockets.
Secrets and personal submission documents are excluded from the image.

To use the original local model explicitly, set
`STUDYBUDDY_PROVIDER=lmstudio`, start LM Studio's server, and load Qwen 2.5 7B
Instruct as `qwen2.5-7b-instruct`. Its optional settings are
`LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, and `LMSTUDIO_TIMEOUT`. A cloud app
cannot use a visitor's laptop `localhost` as its inference server.

References:

- [Deploy on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Groq structured outputs](https://console.groq.com/docs/structured-outputs)
- [Groq free-plan rate limits](https://console.groq.com/docs/rate-limits)
