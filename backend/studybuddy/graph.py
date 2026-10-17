"""Model-directed tutoring: observe state, select a tool, execute, and observe again."""

import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import ValidationError

from .agent import TEACHING_TOOLS, decision_context, validate_decision
from .llm import ModelError
from .models import Lesson, TeachingResponse
from .tools import is_repeat, normalize, prepare_notes, retrieve_notes, score_answers, validate_evidence


class StudyState(TypedDict, total=False):
    notes: str
    chunks: list[dict]
    count: int
    difficulty: str
    threshold: int
    max_rounds: int
    round: int
    attempts: int
    lesson: dict
    draft_lesson: dict
    answers: list[int]
    result: dict
    weak_topics: list[str]
    taught_topics: list[str]
    revision: list[dict]
    history: Annotated[list[dict], operator.add]
    trace: Annotated[list[dict], operator.add]
    agent_actions: Annotated[list[dict], operator.add]
    teaching_history: Annotated[list[dict], operator.add]
    validation_errors: list[str]
    model_error: str
    status: str
    phase: str
    decision: str
    action: dict
    agent_steps: int
    observation: str
    coach_note: str
    clarifications: list[str]
    clarification_count: int


def event(node, detail, round_number=1):
    return {"trace": [{"node": node, "detail": detail, "round": round_number}]}


def error_messages(exc):
    if isinstance(exc, ValidationError):
        return [f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()][:5]
    return [str(exc)]


def build_graph(tutor):
    def prepare(state):
        chunks = prepare_notes(state["notes"])
        return {"chunks": chunks, "status": "generating", "phase": "planning", "observation": "Notes have been prepared. Choose the first useful action.", **event("prepare_notes", f"Prepared {len(chunks)} labelled source sections.")}

    def select_action(state):
        feedback = []
        try:
            if state.get("agent_steps", 0) >= 24:
                raise ModelError("The tutor reached its action limit. Please start a new session.")
            for attempt in range(2):
                try:
                    action = validate_decision(tutor.decide(decision_context(state), feedback), state)
                    return {
                        "action": action, "model_error": "", "agent_steps": state.get("agent_steps", 0) + 1,
                        "status": "revision" if action["tool"] == "create_quiz" and state.get("history") and state.get("phase") != "quiz_requested" else state.get("status", "generating"),
                        "agent_actions": [{"round": state["round"], **action}],
                        **event("select_action", f"Selected {action['tool']}: {action['reason']}", state["round"]),
                    }
                except (ValidationError, ValueError) as exc:
                    feedback = error_messages(exc)
            raise ModelError("The tutor could not choose a valid next action: " + "; ".join(feedback))
        except ModelError as exc:
            return {"model_error": str(exc), "validation_errors": [str(exc)], **event("select_action", "No valid action was executed.", state["round"])}

    def route_action(state):
        if state.get("model_error"):
            return "generation_failed"
        tool = state["action"]["tool"]
        if tool in TEACHING_TOOLS:
            return "teach_concepts"
        if tool == "ask_clarification":
            return "await_clarification"
        if tool == "finish":
            return "complete"
        if state.get("history") and state.get("phase") != "quiz_requested":
            return "await_revision"
        return "tutor_agent"

    def tutor_agent(state):
        action = state["action"]
        topics = action["topics"] or state.get("weak_topics", [])
        selected = retrieve_notes(state["chunks"], topics)
        previous = [item["question"] for result in state.get("history", []) for item in result["items"]]
        feedback = list(state.get("validation_errors", []))
        if feedback:
            old_questions = state.get("draft_lesson", {}).get("questions", []) if isinstance(state.get("draft_lesson"), dict) else []
            for item in old_questions[:5]:
                if isinstance(item, dict):
                    feedback.append("Replace invalid or repeated question/options rather than reuse them: " + str({"question": item.get("question"), "options": item.get("options")})[:1000])
        try:
            lesson = tutor.generate(chunks=selected, count=state["count"], difficulty=action["difficulty"], question_style=action["question_style"], round_number=state["round"], weak_topics=topics, previous_questions=previous, feedback=feedback)
            model_error = ""
        except ModelError as exc:
            lesson, model_error = {}, str(exc)
        return {
            "draft_lesson": lesson, "attempts": state.get("attempts", 0) + 1, "model_error": model_error,
            "phase": "quiz_requested", "observation": "Quiz creation returned. Validate it before presenting it.",
            **event("create_quiz", f"Executed selected quiz tool: {action['difficulty']}, {action['question_style']}; {len(selected)} source sections.", state["round"]),
        }

    def validate_quiz(state):
        errors = []
        lesson = None
        if state.get("model_error"):
            errors = [state["model_error"]]
        else:
            try:
                lesson = Lesson.model_validate(state["draft_lesson"]).model_dump()
                errors = validate_evidence(lesson, state["chunks"], state["count"])
                previous = [item["question"] for result in state.get("history", []) for item in result["items"]]
                if tutor.mode != "sample":
                    for index, question in enumerate(lesson["questions"], 1):
                        if is_repeat(question["question"], previous):
                            errors.append(f"Question {index} repeats a previous question: {question['question']}. Replace it with a concrete new scenario, not a definition or a rephrasing.")
            except ValidationError as exc:
                errors = error_messages(exc)
        return {**({"lesson": lesson} if not errors else {}), "validation_errors": errors, "observation": "Quiz validation failed: " + "; ".join(errors) if errors else "Quiz validated; waiting for student answers.", **event("validate_quiz", "Quiz held back: " + "; ".join(errors) if errors else "Schema, options, sources, and question checks passed.", state["round"])}

    def route_validation(state):
        if not state["validation_errors"]:
            return "await_answers"
        if state.get("model_error") or state["attempts"] >= 2:
            return "generation_failed"
        return "select_action"

    def await_answers(state):
        answers = interrupt({"kind": "quiz", "round": state["round"]})
        score_answers(state["lesson"]["questions"], answers)
        return {"answers": answers, **event("await_answers", "Student submitted every answer; resumed the saved graph.", state["round"])}

    def grade(state):
        result = {**score_answers(state["lesson"]["questions"], state["answers"]), "round": state["round"], "difficulty": state["action"]["difficulty"], "question_style": state["action"]["question_style"]}
        return {"result": result, "history": [result], "weak_topics": result["weak_topics"], "taught_topics": [], "revision": [], "phase": "assessed", "status": "reviewing", "observation": f"Scoring tool returned {result['score']}%. Review the actual answers and select the next teaching action.", **event("grade_answers", f"Answer-key scoring: {result['correct']}/{result['total']} = {result['score']}%.", state["round"])}

    def teach_concepts(state):
        action = state["action"]
        topic_keys = {normalize(topic) for topic in action["topics"]}
        mistakes = [item for item in state["result"]["items"] if not item["is_correct"] and normalize(item["topic"]) in topic_keys]
        selected = retrieve_notes(state["chunks"], action["topics"])
        source_ids = {item["source_id"] for item in mistakes}
        selected = list({chunk["id"]: chunk for chunk in selected + [c for c in state["chunks"] if c["id"] in source_ids]}.values())
        sources = {c["id"]: c["text"] for c in selected}
        feedback = []
        try:
            for attempt in range(2):
                try:
                    raw = tutor.teach(chunks=selected, mistakes=mistakes, topics=action["topics"], method=action["tool"], feedback=feedback)
                    cards = TeachingResponse.model_validate(raw).model_dump()["cards"]
                    if len(cards) != len(topic_keys) or {normalize(c["topic"]) for c in cards} != topic_keys:
                        raise ValueError("Return one card per topic without duplicates. Required: " + ", ".join(action["topics"]) + ". Received: " + ", ".join(c["topic"] for c in cards))
                    canonical = {normalize(topic): topic for topic in action["topics"]}
                    for card in cards:
                        if card["source_id"] not in sources:
                            raise ValueError("Choose source IDs only from the supplied notes.")
                        evidence = sources[card["source_id"]]
                        if normalize(card["explanation"]) in normalize(evidence):
                            raise ValueError("Explain the concept in fresh words instead of copying a source passage.")
                        card.update({"topic": canonical[normalize(card["topic"])], "method": action["tool"], "evidence": evidence})
                    return {
                        "revision": state.get("revision", []) + cards,
                        "teaching_history": [{"round": state["round"], **card} for card in cards],
                        "taught_topics": state.get("taught_topics", []) + action["topics"],
                        "observation": f"{action['tool']} completed for {', '.join(action['topics'])}. Teaching cards include new explanations, examples, extra background, and self-check questions. Choose the next useful action.",
                        "model_error": "", "phase": "after_teaching",
                        **event(action["tool"], "Executed model-selected teaching tool for: " + ", ".join(action["topics"]), state["round"]),
                    }
                except (ValidationError, ValueError) as exc:
                    feedback = error_messages(exc)
            raise ModelError("The tutor could not prepare valid concept feedback: " + "; ".join(feedback))
        except ModelError as exc:
            return {"model_error": str(exc), "validation_errors": [str(exc)], **event("teach_concepts", "Personalised feedback failed; no copied-note fallback was substituted.", state["round"])}

    def await_revision(state):
        decision = interrupt({"kind": "revision", "weak_topics": state["weak_topics"], "suggested_difficulty": state["action"]["difficulty"], "question_style": state["action"]["question_style"]})
        if decision not in {"retry", "finish"}:
            raise ValueError("Choose retry or finish.")
        update = {"decision": decision, **event("await_revision", "Student chose " + decision + ".", state["round"])}
        if decision == "retry":
            update.update({"round": state["round"] + 1, "attempts": 0, "validation_errors": [], "status": "generating", "phase": "quiz_requested", "model_error": ""})
        return update

    def await_clarification(state):
        answer = interrupt({"kind": "clarification", "question": state["action"]["question"]})
        validate_clarification(answer)
        chunks = state["chunks"] + [{"id": f"S{len(state['chunks']) + 1:02d}", "text": "Student clarification: " + answer.strip()}]
        return {"chunks": chunks, "clarifications": state.get("clarifications", []) + [answer.strip()], "clarification_count": state.get("clarification_count", 0) + 1, "observation": "Student answered the clarification. Inspect the new context and choose the next action.", **event("ask_clarification", "Student supplied additional context.", state["round"])}

    def complete(state):
        result = state["result"]
        status = "mastered" if result["score"] >= state["threshold"] else "round_limit" if state["round"] >= state["max_rounds"] else "finished"
        return {"status": status, "coach_note": state["action"]["reason"], **event("finish", "Agent recommended finishing: " + state["action"]["reason"], state["round"])}

    def finished(state):
        return {"status": "finished", **event("finished", "Session ended at the student's request.", state["round"])}

    def failed(state):
        return {"status": "error", **event("generation_failed", "Agent stopped with an explicit error; existing scored answers remain available.", state["round"])}

    builder = StateGraph(StudyState)
    nodes = {"prepare_notes": prepare, "select_action": select_action, "tutor_agent": tutor_agent, "validate_quiz": validate_quiz, "await_answers": await_answers, "grade_answers": grade, "teach_concepts": teach_concepts, "await_revision": await_revision, "await_clarification": await_clarification, "complete": complete, "finished": finished, "generation_failed": failed}
    for name, function in nodes.items():
        builder.add_node(name, function)
    builder.add_edge(START, "prepare_notes")
    builder.add_edge("prepare_notes", "select_action")
    builder.add_conditional_edges("select_action", route_action, ["tutor_agent", "teach_concepts", "await_revision", "await_clarification", "complete", "generation_failed"])
    builder.add_edge("tutor_agent", "validate_quiz")
    builder.add_conditional_edges("validate_quiz", route_validation, ["await_answers", "select_action", "generation_failed"])
    builder.add_edge("await_answers", "grade_answers")
    builder.add_edge("grade_answers", "select_action")
    builder.add_conditional_edges("teach_concepts", lambda s: "generation_failed" if s.get("model_error") else "select_action", ["select_action", "generation_failed"])
    builder.add_conditional_edges("await_revision", lambda s: "tutor_agent" if s["decision"] == "retry" else "finished", ["tutor_agent", "finished"])
    builder.add_edge("await_clarification", "select_action")
    for name in ["complete", "finished", "generation_failed"]:
        builder.add_edge(name, END)
    return builder.compile(checkpointer=InMemorySaver())


def graph_config(thread_id):
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": 120}


def start_session(graph, notes, *, thread_id, count=5, difficulty="Standard", threshold=80, max_rounds=3):
    prepare_notes(notes)
    if type(count) is not int or count not in {3, 4, 5}:
        raise ValueError("Choose 3, 4, or 5 questions.")
    if difficulty not in {"Foundation", "Standard", "Challenge"}:
        raise ValueError("Choose a supported difficulty.")
    if threshold not in {60, 80, 100} or type(max_rounds) is not int or not 1 <= max_rounds <= 3:
        raise ValueError("Choose a valid mastery target and 1 to 3 rounds.")
    return graph.invoke({"notes": notes.strip(), "count": count, "difficulty": difficulty, "threshold": threshold, "max_rounds": max_rounds, "round": 1, "attempts": 0, "lesson": {}, "history": [], "trace": [], "agent_actions": [], "teaching_history": [], "agent_steps": 0, "weak_topics": [], "taught_topics": [], "revision": [], "clarifications": [], "clarification_count": 0, "validation_errors": []}, config=graph_config(thread_id))


def submit_answers(graph, thread_id, answers):
    config = graph_config(thread_id)
    snapshot = graph.get_state(config)
    if "await_answers" not in snapshot.next:
        raise ValueError("This session is not currently waiting for quiz answers.")
    score_answers(snapshot.values["lesson"]["questions"], answers)
    return graph.invoke(Command(resume=answers), config=config)


def continue_session(graph, thread_id, decision="retry"):
    if decision not in {"retry", "finish"}:
        raise ValueError("Choose retry or finish.")
    config = graph_config(thread_id)
    if "await_revision" not in graph.get_state(config).next:
        raise ValueError("This session is not currently waiting for a revision decision.")
    return graph.invoke(Command(resume=decision), config=config)


def retry_tutor(graph, thread_id):
    """Retry a stopped model request without grading or discarding answers."""
    config = graph_config(thread_id)
    snapshot = graph.get_state(config)
    state = snapshot.values
    if snapshot.next or state.get("status") != "error" or not state.get("model_error"):
        raise ValueError("This session has no stopped tutor request to retry.")
    if state.get("agent_steps", 0) >= 24:
        raise ValueError("The tutor reached its action limit. Please start a new session.")
    return graph.invoke(Command(
        goto="select_action",
        update={"model_error": "", "validation_errors": [], "attempts": 0,
                "status": "reviewing" if state.get("history") else "generating"},
    ), config=config)


def validate_clarification(answer):
    if not isinstance(answer, str) or not 3 <= len(answer.strip()) <= 1000:
        raise ValueError("Please add a little more detail, using 3 to 1,000 characters.")


def submit_clarification(graph, thread_id, answer):
    validate_clarification(answer)
    config = graph_config(thread_id)
    if "await_clarification" not in graph.get_state(config).next:
        raise ValueError("This session is not waiting for clarification.")
    return graph.invoke(Command(resume=answer.strip()), config=config)
