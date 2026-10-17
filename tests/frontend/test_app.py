from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "frontend" / "app.py"


def button(app, label):
    return next(b for b in app.button if b.label == label)


def test_sample_student_flow_in_streamlit():
    app = AppTest.from_file(str(APP)).run()
    assert not app.exception
    button(app, "Try an example").click().run()
    button(app, "Start learning →").click().run()
    assert not app.exception
    button(app, "Check my answers →").click().run()
    assert app.error
    # Radio 0 is the sidebar mode. Quiz radios have stable question keys.
    for widget in app.radio:
        if widget.label.startswith("Answer for question"):
            widget.set_value(0)
    button(app, "Check my answers →").click().run()
    assert not app.exception
    assert app.session_state["state"]["status"] == "revision"
    button(app, "I'm ready · Try a focused quiz →").click().run()
    assert not app.exception
    assert app.session_state["state"]["round"] == 2
    questions = app.session_state["state"]["lesson"]["questions"]
    radios = [r for r in app.radio if r.label.startswith("Answer for question")]
    for widget, question in zip(radios, questions):
        widget.set_value(question["correct_index"])
    button(app, "Check my answers →").click().run()
    assert not app.exception
    assert app.session_state["state"]["status"] == "mastered"
    button(app, "＋ New session").click().run()
    assert not app.exception
    assert "graph" not in app.session_state
