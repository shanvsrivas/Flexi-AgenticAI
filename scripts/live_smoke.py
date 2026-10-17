"""Exercise the configured live tutor and save evidence without API keys."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from studybuddy.export import json_report, markdown_report
from studybuddy.graph import build_graph, continue_session, start_session, submit_answers
from studybuddy.llm import LocalTutor
from studybuddy.sample import SAMPLE_NOTES
from check_model import configured_tutor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=None)
    args = parser.parse_args()
    tutor = LocalTutor(base_url=args.base_url, timeout=300) if args.base_url else configured_tutor()
    graph = build_graph(tutor)
    state = start_session(graph, SAMPLE_NOTES, thread_id="live-verification", count=3)
    print("Initial generation:", state.get("status"), state.get("validation_errors"), flush=True)
    if state.get("status") == "error":
        save(state, tutor)
        raise SystemExit(1)
    # Deliberate scripted mistakes exercise the actual revision branch.
    answers = [(question["correct_index"] + 1) % 4 for question in state["lesson"]["questions"]]
    state = submit_answers(graph, "live-verification", answers)
    print("Scripted wrong answers:", state["result"]["score"], state["status"], flush=True)
    save(state, tutor)
    if state.get("status") == "error":
        raise SystemExit(1)
    assert {c["topic"] for c in state["revision"]} == set(state["weak_topics"])
    assert all(c["example"] and c["extra_info"] and c["explanation"] != c["evidence"] for c in state["revision"])
    print("Agent actions:", [a["tool"] for a in state["agent_actions"]], flush=True)
    while "await_revision" in graph.get_state({"configurable": {"thread_id": "live-verification"}}).next:
        state = continue_session(graph, "live-verification")
        print("Follow-up generation:", state.get("status"), state.get("validation_errors"), flush=True)
        if state.get("status") == "error":
            save(state, tutor)
            raise SystemExit(1)
        state = submit_answers(graph, "live-verification", [q["correct_index"] for q in state["lesson"]["questions"]])
        print("Scripted correct answers:", state["result"]["score"], state["status"], flush=True)
        save(state, tutor)
        if state.get("status") == "error":
            raise SystemExit(1)
    print("Final agent actions:", [a["tool"] for a in state["agent_actions"]], flush=True)
    save(state, tutor)


def save(state, tutor):
    folder = Path(__file__).resolve().parents[1] / "artifacts" / "live-verification"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "session.json").write_text(json_report(state, mode="live", model=tutor.model), encoding="utf-8")
    report = "Verification method: answers were scripted to exercise routing. These scores do not represent a student's learning gain.\n\n"
    (folder / "session.md").write_text(report + markdown_report(state, mode="live", model=tutor.model), encoding="utf-8")


if __name__ == "__main__":
    main()
