"""Streamlit frontend. Run from the project root: python -m streamlit run frontend/app.py"""

import html
import sys
from pathlib import Path
import uuid

import streamlit as st

# Make the backend package available when Streamlit launches this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = str(PROJECT_ROOT / "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from studybuddy.export import markdown_report
from studybuddy.graph import build_graph, continue_session, start_session, submit_answers, submit_clarification
from studybuddy.llm import create_tutor, ModelError
from studybuddy.sample import SAMPLE_NOTES, SampleTutor

st.set_page_config(page_title="StudyBuddy · Learn with a little direction", page_icon="🌱", layout="wide", initial_sidebar_state="auto")
STYLES_PATH = Path(__file__).resolve().parent / "assets" / "styles.css"
st.markdown("<style>" + STYLES_PATH.read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)


def reset_session():
    for key in ["graph", "state", "thread_id", "active_tutor", "active_mode", "active_model"]:
        st.session_state.pop(key, None)


def choose_sample():
    reset_session()
    st.session_state["mode"] = "Example session"
    st.session_state["notes"] = SAMPLE_NOTES


def load_sample():
    st.session_state["notes"] = SAMPLE_NOTES


active = "graph" in st.session_state
with st.sidebar:
    st.markdown('<div class="brand">study<span>buddy</span> 🌱</div><div class="subtle">A little direction. Deeper understanding.</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Make it your own**")
    mode = st.radio("Study with", ["My notes", "Example session"], key="mode", disabled=active)
    sample_mode = mode == "Example session"
    count = st.select_slider("Questions per round", options=[3, 4, 5], value=3, disabled=active)
    difficulty = st.selectbox("Difficulty", ["Standard", "Foundation", "Challenge"], disabled=active or sample_mode)
    threshold = st.select_slider("Score goal", options=[60, 80, 100], value=80, format_func=lambda n: f"{n}%", disabled=active)
    st.caption("Up to 3 practice rounds.")
    if active:
        st.button("＋ New session", on_click=reset_session, width='stretch')

st.markdown('<div class="eyebrow">STUDYBUDDY</div>', unsafe_allow_html=True)
if sample_mode:
    st.markdown('<div class="pill">EXAMPLE SESSION</div>', unsafe_allow_html=True)


def launch(notes):
    try:
        settings = dict(st.secrets) if not sample_mode else {}
    except FileNotFoundError:
        settings = {}
    tutor = SampleTutor() if sample_mode else create_tutor(settings)
    if sample_mode:
        notes = SAMPLE_NOTES
    graph = build_graph(tutor)
    thread_id = str(uuid.uuid4())
    with st.spinner("Preparing your quiz…"):
        state = start_session(graph, notes, thread_id=thread_id, count=count, difficulty="Standard" if sample_mode else difficulty, threshold=threshold)
    st.session_state.update({"graph": graph, "state": state, "thread_id": thread_id, "active_tutor": tutor, "active_mode": tutor.mode, "active_model": tutor.model})
    st.rerun()


if not active:
    st.title("Make your notes stick.")
    st.markdown('<div class="lead">Turn your notes into a quiz, revisit mistakes, and practise what needs work.</div>', unsafe_allow_html=True)
    note_col, info_col = st.columns([1.8, 1], gap="large")
    with note_col:
        st.subheader("Start with what you're learning")
        st.caption("Paste your lecture notes, a topic summary, or a short chapter.")
        if sample_mode:
            notes = st.text_area("Study notes", value=SAMPLE_NOTES, height=260, disabled=True, label_visibility="collapsed")
        else:
            notes = st.text_area("Study notes", key="notes", height=260, placeholder="For example: Photosynthesis converts light energy into chemical energy…", label_visibility="collapsed")
        st.caption(f"{len(notes):,} / 10,000 characters")
        start_col, sample_col = st.columns([1.3, 1])
        if start_col.button("Start learning →", type="primary", width='stretch'):
            try:
                launch(notes)
            except ModelError as exc:
                st.error(str(exc))
            except ValueError as exc:
                st.error(str(exc))
        if not sample_mode:
            sample_col.button("Load example notes", on_click=load_sample, width='stretch')
    with info_col:
        st.markdown('<div class="paper"><div class="paper-title">Less rereading.<br>More understanding.</div><p>A short learning loop that responds to what you actually get right—and what needs another look.</p></div>', unsafe_allow_html=True)
        for n, title, description in [("01", "Bring your notes", "Your notes are the source for the lesson and quiz."), ("02", "Check your understanding", "Answer a short quiz. Every answer has a source quote."), ("03", "Give weak spots another go", "Review mistakes and take a follow-up quiz focused on the gaps.")]:
            st.markdown(f'<div class="step"><b><span class="step-num">{n}</span>{title}</b><p>{description}</p></div>', unsafe_allow_html=True)
        if not sample_mode:
            st.button("Try an example", on_click=choose_sample, width='stretch')
        else:
            st.caption("A ready-made lesson with preset notes and questions.")
else:
    state = st.session_state["state"]
    graph = st.session_state["graph"]
    thread_id = st.session_state["thread_id"]
    pending = graph.get_state({"configurable": {"thread_id": thread_id}}).next
    if state.get("status") == "error" and not state.get("history"):
        st.title("Let's try that again.")
        if state.get("model_error"):
            st.error(state["model_error"])
        else:
            st.error("We couldn't prepare a suitable quiz. Start a new session with a shorter section of notes.")
        with st.expander("More details"):
            st.write(" ".join(state.get("validation_errors", ["Quiz preparation failed."])))
    elif "await_clarification" in pending:
        st.title("One quick question.")
        st.write(state["action"]["question"])
        with st.form("clarification"):
            clarification = st.text_area("Tell your tutor a little more", max_chars=1000)
            clarify_submitted = st.form_submit_button("Continue →", type="primary")
        if clarify_submitted:
            try:
                with st.spinner("Your tutor is preparing the next step…"):
                    st.session_state["state"] = submit_clarification(graph, thread_id, clarification)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    else:
        lesson = state["lesson"]
        st.title(lesson["title"])
        st.markdown(f'<div class="lead">{html.escape(lesson["overview"])}</div>', unsafe_allow_html=True)
        if sample_mode:
            st.caption("You're practising with preset example notes and questions.")
        if state.get("status") == "error":
            st.warning("Your answers are saved, but your tutor couldn't finish the feedback. You can download your summary or start a new session.")
            if "free usage limit" in state.get("model_error", ""):
                st.info(state["model_error"])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Practice round", f"{state['round']} / 3")
        m2.metric("Latest score", f"{state['history'][-1]['score']:g}%" if state.get("history") else "—")
        m3.metric("Score goal", f"{state['threshold']}%")
        m4.metric("Topics to revisit", len(state.get("weak_topics", [])) if state.get("history") else "—")
        st.write("")
        learning_tab, progress_tab = st.tabs(["Learn & practice", "Your progress"])
        with learning_tab:
            if "await_answers" in pending:
                st.subheader(f"Round {state['round']} · Check your understanding")
                st.caption(state["action"]["difficulty"] + " · " + ("Apply what you've learned" if state["action"]["question_style"] == "application" else "Build your foundations"))
                with st.expander("Your quick study guide", expanded=state["round"] == 1):
                    for takeaway in lesson["takeaways"]:
                        st.markdown("- " + takeaway)
                with st.form(f"quiz_{thread_id}_{state['round']}"):
                    answers = []
                    for i, question in enumerate(lesson["questions"]):
                        st.markdown(f"**{i + 1}. {question['question']}**")
                        st.caption(question["topic"])
                        answer = st.radio(f"Answer for question {i + 1}", range(4), index=None, format_func=lambda index, opts=question["options"]: f"{'ABCD'[index]}. {opts[index]}", key=f"{thread_id}_{state['round']}_{i}", label_visibility="collapsed")
                        answers.append(answer)
                        if i < len(lesson["questions"]) - 1:
                            st.divider()
                    submitted = st.form_submit_button("Check my answers →", type="primary", width='stretch')
                if submitted:
                    try:
                        with st.spinner("Your tutor is reviewing your answers…"):
                            st.session_state["state"] = submit_answers(graph, thread_id, answers)
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            elif state.get("history"):
                result = state["result"]
                status = state.get("status")
                if status == "mastered":
                    st.success(f"Goal reached! You scored {result['score']:g}%.")
                elif status == "round_limit":
                    st.info("You've completed three rounds. Use the explanations and source notes below for your next revision session.")
                elif status == "finished":
                    st.info("Nice work today. Download your study summary to keep your progress.")
                elif status != "error":
                    st.subheader("A few concepts need another look." if result["weak_topics"] else "Ready for another challenge?")
                if state.get("coach_note"):
                    st.write(state["coach_note"])
                if state.get("revision"):
                    st.subheader("Let's make these concepts click.")
                    st.caption("Your tutor's explanations include extra background beyond your notes.")
                    methods = {"explain_concept": "A clearer explanation", "worked_example": "Work through an example", "simplify_concept": "Back to the basics"}
                    for card in state["revision"]:
                        with st.container(border=True):
                            st.markdown("**" + card["topic"] + "**")
                            st.caption(methods[card["method"]])
                            st.write(card["misconception"])
                            st.write(card["explanation"])
                            st.markdown("**An example**")
                            st.write(card["example"])
                            st.markdown("**A little more to know**")
                            st.write(card["extra_info"])
                            st.info("Think about it: " + card["check_question"])
                            with st.expander("See the original notes"):
                                st.write(card["evidence"])
                if "await_revision" in pending:
                    st.caption("Up next: " + state["action"]["difficulty"] + " practice · " + ("application questions" if state["action"]["question_style"] == "application" else "core concepts"))
                    retry_col, finish_col = st.columns([1.5, 1])
                    decision = None
                    if retry_col.button("I'm ready · Try a focused quiz →", type="primary", width='stretch'):
                        decision = "retry"
                    if finish_col.button("Finish for now", width='stretch'):
                        decision = "finish"
                    if decision:
                        with st.spinner("Preparing your next round…"):
                            st.session_state["state"] = continue_session(graph, thread_id, decision)
                        st.rerun()
                st.subheader("Your answer review")
                for i, item in enumerate(result["items"], 1):
                    with st.expander(f"{'✓' if item['is_correct'] else '↺'} {i}. {item['question']}", expanded=not item["is_correct"]):
                        st.write("Your answer: " + item["options"][item["selected_index"]])
                        st.write("Correct answer: " + item["options"][item["correct_index"]])
                        st.write(item["explanation"])
                        st.caption("From your notes")
                        st.info(item["evidence"])
        with progress_tab:
            st.subheader("Small steps, visible progress.")
            history = state.get("history", [])
            if history:
                st.dataframe([{"Round": r["round"], "Correct": f"{r['correct']}/{r['total']}", "Score (%)": r["score"], "Topics to revisit": ", ".join(r["weak_topics"]) or "None in this quiz"} for r in history], hide_index=True, width='stretch')
                if len(history) > 1:
                    import pandas as pd
                    st.line_chart(pd.DataFrame({"Round": [r["round"] for r in history], "Score (%)": [r["score"] for r in history]}).set_index("Round"), y_label="Score (%)")
            else:
                st.info("Your results will appear here after you submit the first quiz.")
            st.markdown("**Keep what you've learned**")
            st.caption("Save your answers and revision notes for later.")
            export_args = {"mode": st.session_state["active_mode"], "model": st.session_state["active_model"]}
            st.download_button("↓ Download study summary", markdown_report(state, **export_args, technical_details=False), file_name="studybuddy-summary.md", mime="text/markdown", disabled=not history, width='stretch')

st.markdown('<div class="footer">StudyBuddy · A little practice, every day.</div>', unsafe_allow_html=True)
