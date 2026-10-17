from copy import deepcopy
import json

import pytest

from studybuddy.export import json_report, markdown_report
from studybuddy.graph import build_graph, continue_session, start_session, submit_answers
from studybuddy.llm import LocalTutor, ModelError
from studybuddy.models import Lesson
from studybuddy.sample import SAMPLE_NOTES, SampleTutor
from studybuddy.tools import is_repeat, prepare_notes, retrieve_notes, score_answers, validate_evidence


def start(tutor=None, **kwargs):
    graph = build_graph(tutor or SampleTutor())
    state = start_session(graph, SAMPLE_NOTES, thread_id="test", **kwargs)
    return graph, state


def answers_for(state, mistakes=0):
    answers = [q["correct_index"] for q in state["lesson"]["questions"]]
    for i in range(mistakes):
        answers[i] = (answers[i] + 1) % 4
    return answers


def test_valid_quiz_pauses_without_exposing_answer_key_in_interrupt():
    graph, state = start()
    assert state["validation_errors"] == []
    assert graph.get_state({"configurable": {"thread_id": "test"}}).next == ("await_answers",)
    assert "correct_index" not in str(state["__interrupt__"][0].value)


@pytest.mark.parametrize("mistakes,score,status", [(0, 100, "mastered"), (1, 80, "mastered"), (2, 60, "revision"), (5, 0, "revision")])
def test_score_routes_and_exact_threshold(mistakes, score, status):
    graph, state = start()
    result = submit_answers(graph, "test", answers_for(state, mistakes))
    assert result["result"]["score"] == score
    assert result["status"] == status
    assert len(result["history"]) == 1


def test_revision_resumes_same_graph_and_prioritises_weak_topics():
    graph, state = start(count=3)
    missed = state["lesson"]["questions"][0]["topic"]
    state = submit_answers(graph, "test", answers_for(state, 1))
    assert state["status"] == "revision"  # 2/3 is below 80%.
    assert state["revision"][0]["topic"] == missed
    state = continue_session(graph, "test")
    assert state["round"] == 2
    assert state["lesson"]["questions"][0]["topic"] == missed
    assert len(state["history"]) == 1
    state = submit_answers(graph, "test", answers_for(state))
    assert state["status"] == "mastered"
    assert len(state["history"]) == 2


def test_three_round_limit_prevents_infinite_loop():
    graph, state = start()
    for round_number in range(1, 4):
        state = submit_answers(graph, "test", answers_for(state, 5))
        if round_number < 3:
            state = continue_session(graph, "test")
    assert state["status"] == "round_limit"
    assert len(state["history"]) == 3
    assert not graph.get_state({"configurable": {"thread_id": "test"}}).next


def test_student_can_finish_after_revision():
    graph, state = start()
    submit_answers(graph, "test", answers_for(state, 5))
    state = continue_session(graph, "test", "finish")
    assert state["status"] == "finished"


@pytest.mark.parametrize("answers", [[], [None] * 5, [True] * 5, [4] * 5, ["1"] * 5])
def test_incomplete_or_invalid_answers_leave_checkpoint_untouched(answers):
    graph, _ = start()
    with pytest.raises(ValueError):
        submit_answers(graph, "test", answers)
    snapshot = graph.get_state({"configurable": {"thread_id": "test"}})
    assert snapshot.next == ("await_answers",)
    assert not snapshot.values.get("history")


def test_repeated_submit_does_not_duplicate_results():
    graph, state = start()
    submit_answers(graph, "test", answers_for(state))
    with pytest.raises(ValueError):
        submit_answers(graph, "test", answers_for(state))
    assert len(graph.get_state({"configurable": {"thread_id": "test"}}).values["history"]) == 1


@pytest.mark.parametrize("notes", ["", "Too short", "x" * 10001, "x" * 150])
def test_invalid_notes_rejected(notes):
    with pytest.raises(ValueError):
        prepare_notes(notes)


def test_long_paragraph_chunking_preserves_all_words():
    text = " ".join(f"word{i}" for i in range(650))
    chunks = prepare_notes(text)
    assert " ".join(c["text"] for c in chunks).split() == text.split()
    assert len(chunks) > 1


def test_retrieval_prioritises_relevant_source():
    chunks = prepare_notes(SAMPLE_NOTES)
    assert retrieve_notes(chunks, ["Conditional edges"])[0]["id"] == "S03"


def test_source_quote_and_source_id_are_verified():
    _, state = start()
    lesson = deepcopy(state["lesson"])
    lesson["questions"][0]["evidence"] = "This claim does not occur anywhere in the notes."
    assert "exact quote" in validate_evidence(lesson, state["chunks"], 5)[0]
    lesson["questions"][0]["source_id"] = "UNKNOWN"
    assert "source ID" in validate_evidence(lesson, state["chunks"], 5)[0]


def test_referential_answer_options_are_rejected():
    _, state = start()
    lesson = deepcopy(state["lesson"])
    lesson["questions"][0]["options"][3] = "Both A and B."
    with pytest.raises(ValueError, match="self-contained"):
        Lesson.model_validate(lesson)


def test_slight_rewordings_are_rejected_as_repeats():
    previous = ["In a quiz workflow, how does a conditional edge determine the next node?"]
    assert is_repeat("In a quiz, how does a conditional edge determine the next node?", previous)
    assert not is_repeat("What should the quiz do when a student scores exactly 80 percent?", previous)


class BrokenTutor(SampleTutor):
    def __init__(self, repair=False):
        self.calls = 0
        self.repair = repair

    def generate(self, **kwargs):
        self.calls += 1
        lesson = super().generate(**kwargs)
        if not self.repair or self.calls == 1:
            lesson["questions"][0]["evidence"] = "An invented quotation that is not in the source."
        return lesson


def test_generation_repair_is_bounded():
    tutor = BrokenTutor()
    graph, state = start(tutor)
    assert tutor.calls == 2
    assert state["status"] == "error"
    assert not graph.get_state({"configurable": {"thread_id": "test"}}).next


def test_bad_quote_can_be_repaired_before_showing_quiz():
    tutor = BrokenTutor(repair=True)
    graph, state = start(tutor)
    assert tutor.calls == 2
    assert state["validation_errors"] == []
    assert graph.get_state({"configurable": {"thread_id": "test"}}).next == ("await_answers",)


def test_model_connection_error_has_no_silent_sample_fallback():
    class UnavailableTutor(SampleTutor):
        mode = "live"
        def generate(self, **kwargs):
            raise ModelError("Cannot reach LM Studio.")
    _, state = start(UnavailableTutor())
    assert state["status"] == "error"
    assert state["attempts"] == 1
    assert not state["lesson"]


def test_sessions_are_isolated():
    graph = build_graph(SampleTutor())
    start_session(graph, SAMPLE_NOTES, thread_id="student-a", count=3)
    start_session(graph, SAMPLE_NOTES, thread_id="student-b", count=5)
    assert graph.get_state({"configurable": {"thread_id": "student-a"}}).values["count"] == 3
    assert graph.get_state({"configurable": {"thread_id": "student-b"}}).values["count"] == 5


def test_evidence_export_contains_actual_results_and_mode():
    graph, state = start()
    state = submit_answers(graph, "test", answers_for(state, 2))
    data = json.loads(json_report(state, mode="sample", model="fixture"))
    assert data["history"][0]["score"] == 60
    assert "api_key" not in data
    report = markdown_report(state, mode="sample", model="fixture")
    assert "No LLM was called" in report
    assert "60.0%" in report
    assert "Source notes" in report


def test_local_client_sends_json_schema_and_parses_lesson(monkeypatch):
    _, state = start(count=3)
    def request(method, url, **kwargs):
        assert method == "POST"
        assert url == "http://localhost:1234/v1/chat/completions"
        assert kwargs["json"]["response_format"]["type"] == "json_schema"
        assert kwargs["json"]["model"] == "qwen2.5-7b-instruct"
        assert kwargs["headers"]["Authorization"] == "Bearer local-test-token"
        class Response:
            ok = True
            def json(self):
                return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(state["lesson"])}}]}
        return Response()
    monkeypatch.setattr("studybuddy.llm.requests.request", request)
    tutor = LocalTutor(model="qwen2.5-7b-instruct", api_key="local-test-token")
    lesson = tutor.generate(chunks=state["chunks"], count=3, difficulty="Standard", round_number=1, weak_topics=[], previous_questions=[], feedback=[])
    assert Lesson.model_validate(lesson).title
    assert lesson["questions"][0]["evidence"] == state["chunks"][0]["text"]


def test_model_http_error_does_not_leak_token_or_server_body(monkeypatch):
    class Response:
        ok = False
        status_code = 401
        text = "sensitive-server-message"
    monkeypatch.setattr("studybuddy.llm.requests.request", lambda *a, **kw: Response())
    tutor = LocalTutor(api_key="secret-token")
    with pytest.raises(ModelError) as error:
        tutor.list_models()
    assert "secret-token" not in str(error.value)
    assert "sensitive-server-message" not in str(error.value)


@pytest.mark.parametrize("base_url", ["file:///data", "http://user:secret@localhost/v1", "http://localhost/v1?token=secret"])
def test_url_rejects_embedded_credentials(base_url):
    with pytest.raises(ValueError):
        LocalTutor(base_url=base_url)
