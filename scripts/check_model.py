"""Check model discovery and a real structured response without logging secrets."""

import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from studybuddy.llm import create_tutor, ModelError


def configured_tutor():
    secret_path = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    settings = tomllib.loads(secret_path.read_text(encoding="utf-8")) if secret_path.exists() else {}
    return create_tutor(settings)


def check_model():
    tutor = configured_tutor()
    if tutor.model not in tutor.list_models():
        raise ModelError(f"The configured service does not expose {tutor.model}.")
    schema = {
        "type": "object",
        "properties": {"status": {"type": "string", "enum": ["ready"]}},
        "required": ["status"],
        "additionalProperties": False,
    }
    result = tutor._structured(
        "This is a connection check. Return status ready using the supplied JSON schema.",
        {"check": "structured_output"}, schema, "deployment_check", 100,
    )
    if result != {"status": "ready"}:
        raise ModelError("The model endpoint did not produce the required structured response.")
    return tutor.model


if __name__ == "__main__":
    try:
        model = check_model()
    except (ModelError, ValueError) as exc:
        # ModelError messages exclude the endpoint's access token and response body.
        print(f"Model check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Model ready: {model}; model discovery and structured output passed.")
