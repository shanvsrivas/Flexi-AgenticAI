"""Portable evidence exports, with no connection credentials."""

import json
from datetime import datetime
from zoneinfo import ZoneInfo


def session_data(state, *, mode, model):
    return {
        "project": "StudyBuddy",
        "exported_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        "mode": mode,
        "model": model,
        "status": state.get("status"),
        "target": state.get("threshold"),
        "difficulty": state.get("difficulty"),
        "history": state.get("history", []),
        "workflow_trace": state.get("trace", []),
        "source_sections": state.get("chunks", []),
        "validation_errors": state.get("validation_errors", []),
        "agent_actions": state.get("agent_actions", []),
        "teaching_history": state.get("teaching_history", []),
    }


def json_report(state, *, mode, model):
    return json.dumps(session_data(state, mode=mode, model=model), indent=2, ensure_ascii=False)


def markdown_report(state, *, mode, model, technical_details=True):
    data = session_data(state, mode=mode, model=model)
    if technical_details:
        lines = ["# StudyBuddy — session evidence", "", f"Date: {data['exported_at']}", f"Mode: {mode}", f"Model: {model}", f"Status: {data['status']}", f"Session target: {data['target']}%", "", "This is an automatically recorded practice session, not a claim of general learning mastery.", ""]
    else:
        lines = ["# Your StudyBuddy summary", "", f"Date: {data['exported_at'][:10]}", f"Score goal: {data['target']}%", ""]
    if mode == "sample":
        lines += ["**Sample mode used fixed authored questions. No LLM was called.**" if technical_details else "Example session with preset notes and questions.", ""]
    for result in data["history"]:
        lines += [f"## Round {result['round']}", "", f"Score: {result['correct']}/{result['total']} ({result['score']}%)", "Weak topics: " + (", ".join(result["weak_topics"]) or "None in this quiz"), ""]
        for index, item in enumerate(result["items"], 1):
            source_label = f"Source: {item['source_id']}" if technical_details else "From your notes:"
            lines += [f"### {index}. {item['question']}", "", f"Selected: {item['options'][item['selected_index']]}", f"Correct: {item['options'][item['correct_index']]}", f"Result: {'Correct' if item['is_correct'] else 'Incorrect'}", f"Explanation: {item['explanation']}", source_label, f"> {item['evidence']}", ""]
        cards = [card for card in data["teaching_history"] if card["round"] == result["round"]]
        if cards:
            lines += ["### Concepts to revisit", "", "Tutor explanations include background information beyond the supplied notes.", ""]
            for card in cards:
                lines += [f"#### {card['topic']}", "", card["misconception"], "", card["explanation"], "", "Example: " + card["example"], "", "Extra insight: " + card["extra_info"], "", "Self-check: " + card["check_question"], ""]
    if technical_details:
        lines += ["## Agent-selected actions", ""]
        for action in data["agent_actions"]:
            lines += [f"- Round {action['round']} · {action['tool']} ({action['difficulty']}, {action['question_style']}): {action['reason']}"]
        lines += ["## Workflow trace", ""]
        for item in data["workflow_trace"]:
            lines += [f"- Round {item['round']} · {item['node']}: {item['detail']}"]
        lines += ["", "## Source notes", ""]
        for chunk in data["source_sections"]:
            lines += [f"### {chunk['id']}", "", chunk["text"], ""]
    return "\n".join(lines)
