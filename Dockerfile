FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 1000 studybuddy

COPY backend ./backend
COPY frontend ./frontend
COPY .streamlit/config.toml ./.streamlit/config.toml
COPY scripts/check_model.py ./scripts/check_model.py

USER studybuddy
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://127.0.0.1:8501/_stcore/health', timeout=3).raise_for_status()"

CMD ["python", "-m", "streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
