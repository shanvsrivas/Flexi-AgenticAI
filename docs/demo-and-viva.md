# Demonstration and viva guide

## A three-to-five-minute demonstration

1. **Problem, 20 seconds.** Explain that students need to identify weak concepts rather than only reread notes.
2. **Setup, 20 seconds.** Choose My notes. Explain that Qwen 2.5 7B Instruct runs through a server-configured connection; users do not select models or enter connection details.
3. **Notes and generation, 30–60 seconds.** Load example notes or paste short notes. Select three questions for a faster live generation. Build the session. Read the guide and show the quiz.
4. **Feedback, 30–60 seconds.** Submit answers and show a missed concept's explanation, worked example, extra insight, and self-check. Expand the original notes to show that they are separate. If using deliberate mistakes, identify them as test inputs. Even a passing score receives feedback for individual mistakes.
5. **Agent decision, 30–60 seconds.** Explain which teaching method the agent selected and its recommended next difficulty/style. If it offers another quiz, accept it. The agent may recommend finishing instead; show that choice honestly rather than claiming a fixed route.
6. **Evidence, 30 seconds.** Open Your progress and download the study summary. For the technical explanation, show `docs/diagrams/workflow.mmd` and the saved trace in `artifacts/live-verification/session.json`. These stay outside the student-facing screens.
7. **Limitations, 20 seconds.** State that question correctness still needs review, quotes only establish source presence, and session memory does not survive restarts.

If the model is unavailable, choose **Example session** or click **Try an example**. This demonstrates the real graph, scoring, and interface using fixed content. It does not demonstrate live generation. The saved live verification artifacts provide a separate record of a real Qwen run.

## Useful explanations to practise

**Why use LangGraph?**

The app needs to execute model-selected actions, return tool observations to the agent, remember the current quiz, and pause for student answers or clarification. A state graph makes this tool loop and its bounds explicit.

**Where is the AI agent?**

`LocalTutor.decide` observes state and selects an allowed tool and arguments. It can select explanation, worked example, simplification, clarification, another quiz, or finishing. LangGraph executes the selected tool and sends its result back as an observation. This is genuine model-directed action selection within a controlled scope.

**What is state?**

The shared data passed between nodes: notes, source sections, generated lesson, answers, latest score, weak topics, round number, history, and trace. See `StudyState` in `backend/studybuddy/graph.py`.

**What is a conditional edge?**

It chooses the next node from state. `route_action` dispatches the tool selected by Qwen. For example, worked_example executes teaching; ask_clarification pauses for context; finish ends the session. Validation and session limits remain rules in Python.

**How does the graph wait for me?**

`interrupt()` pauses the graph and saves its state through `InMemorySaver`. The app resumes with `Command(resume=...)` and the same thread ID.

**Why not ask the LLM to score answers?**

For multiple-choice questions, comparing indices against an answer key is simpler, reproducible, and avoids an extra inference call. This still depends on the model having generated a correct answer key.

**Does this use RAG?**

It retrieves labelled note sections with lexical matching and supplies them as context. It does not use embeddings, a vector database, or a large-document RAG pipeline.

**How do you prevent unsupported answers?**

The prompt constrains generation to notes. The model selects a source ID, and the application attaches the original source section verbatim. This avoids asking a small model to reproduce exact quotations. It does not prove that the selected section supports the chosen answer. Human review remains necessary.

Extra teaching can include relevant background beyond the notes and is labelled separately. It is generated knowledge, not independently verified research. Quiz questions remain restricted to source notes.

**How is this different from a fixed workflow?**

A fixed score rule would always select the same next action for a given score. Here Qwen receives actual answers, previous teaching, and tool observations, then chooses the next tool and its arguments. It can choose a simpler explanation or an application example at the same score, alter the next quiz's difficulty, or offer further practice after reaching the target. Python checks that the selected action is permitted.

**Does the model use native function calling?**

It uses structured JSON containing a tool name and arguments. A validated LangGraph dispatcher executes that selection. This provides model-directed tool use without relying on the provider's native `tool_calls` format.

**Does it have multiple agents?**

No. It has one tutor agent and multiple graph nodes. A node is a workflow step, not automatically an independent agent.

**What happens if generation fails?**

Malformed or ungrounded output gets one repair attempt. Persistent failure or an unavailable model produces an error. There is no silent switch to sample mode.

**What would you improve next?**

Persistent checkpoints, reviewed question banks, stronger checks of evidence support, semantic duplicate detection, and file uploads. Describe these as future improvements, not current features.

## Before submission

- Fill in roll number, class, date, and final repository/deployment links.
- Attach the actual course certificates with their actual durations.
- Replace reflection prompts with your own observations.
- Read and understand the graph and scoring functions.
- Keep screenshots and exported evidence from your own demonstration.
- Disclose AI assistance according to your teacher's requirements.
