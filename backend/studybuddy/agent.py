"""Tool catalogue and execution rules for a model-directed tutoring loop."""

from .models import AgentDecision
from .tools import normalize

TEACHING_TOOLS = {"explain_concept", "worked_example", "simplify_concept"}
TOOL_DESCRIPTIONS = {
    "create_quiz": "Create a new quiz; select difficulty, focus topics, and recall or application questions.",
    "explain_concept": "Teach missed concepts in new words, compare the mistaken and correct answers, and add background information.",
    "worked_example": "Teach missed concepts through a concrete worked example or real-life application, with extra background.",
    "simplify_concept": "Rebuild missed concepts using simpler language and an everyday analogy, with extra background.",
    "ask_clarification": "Ask one specific question when the study notes are unclear or lack enough useful context.",
    "finish": "Recommend ending after reviewing the results and any required feedback; does not invent a passing score.",
}


def uncovered_topics(state):
    taught = {normalize(topic) for topic in state.get("taught_topics", [])}
    return [topic for topic in state.get("weak_topics", []) if normalize(topic) not in taught]


def available_tools(state):
    if state.get("phase") == "quiz_requested":
        return ["create_quiz"]
    if not state.get("history"):
        tools = ["create_quiz"]
        if state.get("clarification_count", 0) < 2:
            tools.append("ask_clarification")
        return tools
    if uncovered_topics(state):
        return sorted(TEACHING_TOOLS)
    tools = ["finish"]
    if state["round"] < state["max_rounds"]:
        tools.insert(0, "create_quiz")
    return tools


def decision_context(state):
    """Provide observable facts and tool results, not private chain-of-thought."""
    latest = state.get("result", {})
    return {
        "sources": state["chunks"],
        "round": state["round"],
        "max_rounds": state["max_rounds"],
        "requested_difficulty": state["difficulty"],
        "score_goal": state["threshold"],
        "score_history": [{"round": r["round"], "score": r["score"]} for r in state.get("history", [])],
        "latest_answers": [{"topic": q["topic"], "question": q["question"], "student_answer": q["options"][q["selected_index"]], "correct_answer": q["options"][q["correct_index"]], "correct": q["is_correct"]} for q in latest.get("items", [])],
        "unreviewed_topics": uncovered_topics(state),
        "previous_teaching": [{"topic": c["topic"], "method": c["method"], "explanation": c["explanation"]} for c in state.get("revision", [])],
        "tool_observation": state.get("observation", "No tool has run yet."),
        "clarifications": state.get("clarifications", []),
        "validation_feedback": state.get("validation_errors", []),
        "allowed_tools": [{"name": name, "description": TOOL_DESCRIPTIONS[name]} for name in available_tools(state)],
    }


def validate_decision(raw, state):
    decision = AgentDecision.model_validate(raw).model_dump()
    if decision["tool"] not in available_tools(state):
        raise ValueError("Choose one of the currently allowed tools. Missed concepts need feedback before another quiz or finishing.")
    if decision["tool"] in TEACHING_TOOLS:
        valid = {normalize(topic): topic for topic in uncovered_topics(state)}
        if not decision["topics"] or any(normalize(topic) not in valid for topic in decision["topics"]):
            raise ValueError("Teaching topics must be copied from unreviewed_topics.")
        decision["topics"] = list(dict.fromkeys(valid[normalize(topic)] for topic in decision["topics"]))
    if decision["tool"] == "ask_clarification" and len(decision["question"]) < 10:
        raise ValueError("Ask a specific clarification question of at least 10 characters.")
    return decision
