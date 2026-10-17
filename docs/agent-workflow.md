# How StudyBuddy uses an AI agent

StudyBuddy gives Qwen 2.5 7B Instruct control over a bounded set of teaching actions. The graph does not automatically map every score to the same next action.

1. Prepare notes and provide the available tools and current session state.
2. Qwen selects one tool, its arguments, and a brief action justification.
3. Python validates that the tool and arguments are allowed at this stage.
4. LangGraph executes the selection and records its result as an observation.
5. Qwen observes that result and selects the next useful action.
6. Pause whenever the student must answer a quiz, provide clarification, or agree to another quiz.

## What the model controls

| Selected action | What executes |
|---|---|
| `create_quiz` | Retrieve relevant note sections and generate a quiz at the selected difficulty and recall/application style |
| `explain_concept` | Explain the missed concept, compare mistaken and correct answers, and add an example and extra insight |
| `worked_example` | Teach the concept through a concrete application or worked scenario |
| `simplify_concept` | Rebuild the concept in simpler language with an everyday analogy |
| `ask_clarification` | Ask a specific question and wait for the student's additional context |
| `finish` | Recommend ending; the recorded score determines whether the goal was reached |

The same score can lead to different teaching methods. A model can also recommend an application challenge after a perfect score or recommend finishing below the score goal after providing feedback. These are permitted choices, not guaranteed behaviours in every run.

## What Python controls

- Correct answer-index scoring and validation of submitted answers.
- Permitted tools at each stage and validation of tool arguments.
- Feedback for every missed concept before another quiz or finishing.
- At most three quizzes, two clarifications, and 24 agent decisions.
- Bounded repairs and explicit failures without silent sample substitution.
- Source copying, state isolation, and saving decision/teaching history.

## Extra concept information

Teaching cards contain a possible misconception, a fresh explanation, a concrete example, extra background, and an open-ended self-check prompt. The original source is collapsed separately. The model can use established background knowledge for these explanations; the app does not claim the additional information was found in the student's notes or independently fact-checked. Quiz generation remains based on the supplied notes.

## Protocol and evidence

The model returns schema-constrained JSON describing a tool selection. A graph dispatcher executes it. This is a custom structured tool protocol, not the provider's native `tool_calls` API.

Inspect `backend/studybuddy/agent.py` for the catalogue and policies, `llm.py` for decision and teaching prompts, and `graph.py` for execution. Actual action names, arguments, brief justifications, tool observations, and expanded explanations are saved in `artifacts/live-verification/session.json`.

Example mode uses fixed authored fixtures for both decisions and content; it demonstrates the executor but not live model autonomy. Use My notes with the Qwen server running to demonstrate the real agent.
