from copy import deepcopy

import pytest

from studybuddy.agent import available_tools
from studybuddy.export import json_report, markdown_report
from studybuddy.graph import build_graph, continue_session, retry_tutor, start_session, submit_answers, submit_clarification
from studybuddy.llm import ModelError
from studybuddy.sample import SAMPLE_NOTES, SampleTutor


def setup(tutor, count=3):
    graph = build_graph(tutor)
    state = start_session(graph, SAMPLE_NOTES, thread_id="agent-test", count=count)
    return graph, state


def wrong_answers(state):
    return [(q["correct_index"] + 1) % 4 for q in state["lesson"]["questions"]]


def test_connection_retry_keeps_scored_answers_and_recovers_teaching():
    class TransientTutor(SampleTutor):
        unavailable = True

        def teach(self, **kwargs):
            if self.unavailable:
                raise ModelError("The tutor has reached its shared free usage limit.")
            return super().teach(**kwargs)

    tutor = TransientTutor()
    graph, state = setup(tutor)
    answers = wrong_answers(state)
    failed = submit_answers(graph, "agent-test", answers)
    assert failed["status"] == "error" and len(failed["history"]) == 1
    tutor.unavailable = False
    recovered = retry_tutor(graph, "agent-test")
    assert recovered["status"] == "revision"
    assert recovered["round"] == 1 and recovered["answers"] == answers
    assert recovered["history"] == failed["history"]
    assert len(recovered["revision"]) == 3
    assert graph.get_state({"configurable": {"thread_id": "agent-test"}}).next == ("await_revision",)


def test_connection_retry_recovers_initial_quiz_but_rejects_an_active_quiz():
    class TransientTutor(SampleTutor):
        unavailable = True

        def generate(self, **kwargs):
            if self.unavailable:
                raise ModelError("The tutor could not connect.")
            return super().generate(**kwargs)

    tutor = TransientTutor()
    graph, state = setup(tutor)
    assert state["status"] == "error" and not state["history"]
    tutor.unavailable = False
    recovered = retry_tutor(graph, "agent-test")
    assert recovered["lesson"] and not recovered["history"]
    with pytest.raises(ValueError, match="no stopped tutor request"):
        retry_tutor(graph, "agent-test")


class ChoosingTutor(SampleTutor):
    """A model stand-in chooses a different real tool at the same score."""
    def __init__(self, method="worked_example", stop=False):
        self.method, self.stop = method, stop
        self.executed = []
        self.contexts = []
        self.quiz_arguments = []

    def decide(self, context, feedback):
        self.contexts.append(deepcopy(context))
        decision = super().decide(context, feedback)
        if decision["tool"] == "explain_concept":
            decision["tool"] = self.method
        elif self.stop and context["score_history"] and not context["unreviewed_topics"]:
            decision["tool"] = "finish"
        if context["score_history"]:
            decision.update({"difficulty": "Foundation", "question_style": "application"})
        return decision

    def teach(self, **kwargs):
        self.executed.append(kwargs["method"])
        return super().teach(**kwargs)

    def generate(self, **kwargs):
        self.quiz_arguments.append(deepcopy(kwargs))
        return super().generate(**kwargs)


@pytest.mark.parametrize("method", ["worked_example", "simplify_concept", "explain_concept"])
def test_model_chosen_teaching_tool_is_executed_at_same_score(method):
    tutor = ChoosingTutor(method)
    graph, state = setup(tutor)
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    assert state["result"]["score"] == 0
    assert tutor.executed == [method]
    assert {c["method"] for c in state["revision"]} == {method}
    assert all(c["example"] and c["extra_info"] and c["check_question"] for c in state["revision"])
    assert all(c["explanation"] != c["evidence"] for c in state["revision"])
    assert "completed" in tutor.contexts[-1]["tool_observation"]
    state = continue_session(graph, "agent-test")
    assert tutor.quiz_arguments[-1]["difficulty"] == "Foundation"
    assert tutor.quiz_arguments[-1]["question_style"] == "application"


def test_agent_may_recommend_stopping_below_goal_without_claiming_mastery():
    graph, state = setup(ChoosingTutor(stop=True))
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    assert state["status"] == "finished"
    assert state["result"]["score"] == 0
    assert len(state["revision"]) == 3


def test_agent_can_choose_an_application_challenge_even_after_a_perfect_score():
    class ChallengeTutor(SampleTutor):
        def decide(self, context, feedback):
            decision = super().decide(context, feedback)
            if context["score_history"] and context["round"] == 1:
                decision.update({"tool": "create_quiz", "difficulty": "Challenge", "question_style": "application"})
            return decision
    graph, state = setup(ChallengeTutor())
    state = submit_answers(graph, "agent-test", [q["correct_index"] for q in state["lesson"]["questions"]])
    assert state["result"]["score"] == 100
    assert state["status"] == "revision"
    assert state["action"]["difficulty"] == "Challenge"
    assert graph.get_state({"configurable": {"thread_id": "agent-test"}}).next == ("await_revision",)


def test_invalid_tool_selection_never_executes_a_generation_tool():
    class InvalidTutor(SampleTutor):
        def decide(self, context, feedback):
            return {"tool": "unsupported_action"}
        def generate(self, **kwargs):
            raise AssertionError("An invalid plan must not execute a tool.")
    _, state = setup(InvalidTutor())
    assert state["status"] == "error"
    assert not state["agent_actions"]


def test_missed_concept_is_taught_even_when_score_meets_goal():
    graph, state = setup(SampleTutor(), count=5)
    answers = [q["correct_index"] for q in state["lesson"]["questions"]]
    answers[0] = (answers[0] + 1) % 4
    state = submit_answers(graph, "agent-test", answers)
    assert state["status"] == "mastered"
    assert state["result"]["score"] == 80
    assert len(state["revision"]) == 1
    assert state["agent_actions"][-2]["tool"] == "explain_concept"


def test_invalid_agent_action_cannot_skip_feedback_and_results_survive():
    class SkippingTutor(SampleTutor):
        def decide(self, context, feedback):
            result = super().decide(context, feedback)
            if context["unreviewed_topics"]:
                result["tool"] = "finish"
            return result
    graph, state = setup(SkippingTutor())
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    assert state["status"] == "error"
    assert state["history"][0]["score"] == 0
    assert not state["revision"]
    assert "finish" not in [a["tool"] for a in state["agent_actions"]]


def test_copied_note_feedback_is_retried_then_rejected():
    class CopyingTutor(SampleTutor):
        def __init__(self):
            self.calls = 0
        def teach(self, **kwargs):
            self.calls += 1
            result = super().teach(**kwargs)
            sources = {c["id"]: c["text"] for c in kwargs["chunks"]}
            for card in result["cards"]:
                card["explanation"] = sources[card["source_id"]]
            return result
    tutor = CopyingTutor()
    graph, state = setup(tutor)
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    assert state["status"] == "error"
    assert tutor.calls == 2
    assert not state["revision"]


def test_teaching_connection_failure_never_falls_back_to_copied_notes():
    class FailingTutor(SampleTutor):
        def teach(self, **kwargs):
            raise ModelError("Teaching service unavailable.")
    graph, state = setup(FailingTutor())
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    assert state["status"] == "error"
    assert len(state["history"]) == 1
    assert not state["revision"]


def test_failed_follow_up_keeps_previous_valid_quiz_and_results():
    class BrokenFollowUp(SampleTutor):
        def generate(self, **kwargs):
            return {} if kwargs["round_number"] > 1 else super().generate(**kwargs)
    graph, state = setup(BrokenFollowUp())
    title = state["lesson"]["title"]
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    state = continue_session(graph, "agent-test")
    assert state["status"] == "error"
    assert state["lesson"]["title"] == title
    assert state["history"][0]["score"] == 0


class ClarifyingTutor(SampleTutor):
    def decide(self, context, feedback):
        decision = super().decide(context, feedback)
        if not context["clarifications"]:
            decision.update({"tool": "ask_clarification", "question": "Which part of these notes would you most like to practise?"})
        return decision


def test_model_can_pause_for_clarification_and_resume_with_new_context():
    graph, state = setup(ClarifyingTutor())
    assert graph.get_state({"configurable": {"thread_id": "agent-test"}}).next == ("await_clarification",)
    with pytest.raises(ValueError):
        submit_clarification(graph, "agent-test", " ")
    state = submit_clarification(graph, "agent-test", "Please focus on graph state and conditional edges.")
    assert state["clarification_count"] == 1
    assert state["chunks"][-1]["text"].startswith("Student clarification:")
    assert graph.get_state({"configurable": {"thread_id": "agent-test"}}).next == ("await_answers",)


def test_clarification_limit_and_round_limit_remove_unavailable_actions():
    assert available_tools({"phase": "planning", "history": [], "clarification_count": 2}) == ["create_quiz"]
    assert available_tools({"history": [1], "weak_topics": [], "round": 3, "max_rounds": 3}) == ["finish"]


def test_export_preserves_teaching_after_next_round_and_hides_action_log_for_students():
    graph, state = setup(SampleTutor())
    state = submit_answers(graph, "agent-test", wrong_answers(state))
    state = continue_session(graph, "agent-test")
    state = submit_answers(graph, "agent-test", [q["correct_index"] for q in state["lesson"]["questions"]])
    assert len(state["teaching_history"]) == 3
    evidence = json_report(state, mode="sample", model="fixture")
    assert '"agent_actions"' in evidence and '"teaching_history"' in evidence
    summary = markdown_report(state, mode="sample", model="fixture", technical_details=False)
    assert "Extra insight:" in summary and "Agent-selected actions" not in summary
