import json

import pytest
import requests

from studybuddy.llm import GROQ_MODEL, GroqTutor, LocalTutor, ModelError, create_tutor
from studybuddy.models import AgentDecision


def test_groq_requires_a_key_and_does_not_fall_back(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("STUDYBUDDY_PROVIDER", raising=False)
    with pytest.raises(ModelError, match="not been connected"):
        create_tutor()
    assert isinstance(create_tutor({"STUDYBUDDY_PROVIDER": "lmstudio"}), LocalTutor)
    with pytest.raises(ValueError):
        create_tutor({"STUDYBUDDY_PROVIDER": "unknown"})


def test_groq_agent_uses_private_key_fixed_model_and_strict_schema(monkeypatch):
    action = {
        "tool": "create_quiz", "topics": [], "difficulty": "Standard",
        "question_style": "recall", "reason": "Check the student's starting understanding.", "question": "",
    }

    def request(method, url, **kwargs):
        assert method == "POST"
        assert url == "https://api.groq.com/openai/v1/chat/completions"
        assert kwargs["headers"]["Authorization"] == "Bearer private-test-key"
        body = kwargs["json"]
        assert body["model"] == GROQ_MODEL
        assert body["reasoning_effort"] == "low"
        schema = body["response_format"]["json_schema"]
        assert schema["strict"] is True
        assert schema["schema"]["additionalProperties"] is False
        assert set(schema["schema"]["required"]) == set(action)
        assert "private-test-key" not in json.dumps(body)

        class Response:
            ok = True

            def json(self):
                return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(action)}}]}

        return Response()

    monkeypatch.setattr("studybuddy.llm.requests.request", request)
    tutor = create_tutor({"GROQ_API_KEY": "private-test-key"})
    assert isinstance(tutor, GroqTutor)
    assert AgentDecision.model_validate(tutor.decide({}, [])).tool == "create_quiz"


@pytest.mark.parametrize("status", [400, 401, 403, 404, 413, 429, 500])
def test_groq_errors_never_include_credentials_or_provider_body(monkeypatch, status):
    class Response:
        ok = False
        status_code = status
        text = "private-provider-body"

    monkeypatch.setattr("studybuddy.llm.requests.request", lambda *a, **kw: Response())
    with pytest.raises(ModelError) as error:
        GroqTutor(api_key="private-test-key").list_models()
    assert "private-test-key" not in str(error.value)
    assert "private-provider-body" not in str(error.value)
    if status == 429:
        assert "free usage limit" in str(error.value)


def test_groq_timeout_is_safe_and_bounded(monkeypatch):
    def request(*args, **kwargs):
        assert kwargs["timeout"] == (5, 90)
        raise requests.Timeout("private-test-key")

    monkeypatch.setattr("studybuddy.llm.requests.request", request)
    with pytest.raises(ModelError, match="took too long") as error:
        GroqTutor(api_key="private-test-key").list_models()
    assert "private-test-key" not in str(error.value)
