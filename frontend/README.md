# Frontend

- `app.py`: Streamlit screen, settings, quiz controls, feedback, progress, and downloads.
- `assets/styles.css`: Interface styling, separated from Python code.

Launch from the **AgenticAI project root** with `run.ps1`, or:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py --server.headless true
```

The frontend imports the `studybuddy` package from the sibling `backend` source folder. Styles load relative to this file, and Streamlit reads shared configuration from the project-root `.streamlit` folder.
