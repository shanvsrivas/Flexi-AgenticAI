# StudyBuddy: An Adaptive AI Learning Assistant Using LangGraph

**Submission draft — review and personalise before submitting.**

Student: Shanvi Srivastava  
Roll number / class / section: [Fill in]  
Subject: Artificial Intelligence  
Submission date: [Fill in]

## 1. Project overview

StudyBuddy uses a tutoring agent to select useful learning actions from a student's notes and quiz performance. It can create a quiz, explain a missed concept, work through an example, simplify an explanation, ask a clarification question, or recommend finishing. Feedback includes new explanations and relevant background information rather than only repeating source notes. The current default model is GPT-OSS 20B through Groq; the earlier local version used Qwen through LM Studio.

## 2. Understanding of agentic AI

An AI agent uses observations to choose actions towards a goal and inspects the results of those actions. In StudyBuddy, the model observes notes, actual selected answers, scores, previous teaching, and the latest tool result. It selects an allowed tool and arguments, including topics, difficulty, and recall or application questions. LangGraph executes the choice and returns the tool's result to the agent for its next decision.

LangGraph represents the workflow using shared state, nodes, and conditional edges. The state stores notes, quizzes, answers, scores, teaching cards, model-selected actions, and observations. Conditional edges dispatch the tool selected by the model. Interrupts pause for quiz answers, clarification, or permission to take another quiz. The score is an observation and a goal indicator, rather than a fixed rule selecting every next action.

This is one agent with bounded autonomy, not a multi-agent system. Tool selection uses a schema-constrained JSON protocol; it does not use the provider's native `tool_calls` format. The chosen tool name and arguments determine which operation executes. Python enforces valid actions, feedback coverage, scoring, and execution limits.

## 3. Courses completed

| Course | Provider | Instructors | Certificate duration | Completion date |
|---|---|---|---|---|
| AI Agents & AI Automation — The Practical Agentic AI Guide | Udemy | Nikolai Schuler, Simon Coton | 8 hours | September 12, 2026 |
| Agentic AI for Beginners: Build AI Agents with LangGraph | Udemy | Aakriti E-Learning Academy | 10 hours | September 12, 2026 |

Completion evidence: attach the two supplied certificates.

The certificates show 18 hours combined. The supplied form mentions a minimum of 45 hours; clarify that requirement with the teacher and record the actual course durations.

### Application of learning

- Agent goals and feedback: observe tool results and choose the next teaching action.
- Tools and automation: execute model-selected explanations, worked examples, simplification, quizzes, clarification, and completion.
- LangGraph state: preserve information across nodes and practice rounds.
- Conditional edges: dispatch the model-selected tool and enforce validation and session limits.
- Human input: interrupt the graph for answers and resume it using the same thread ID.

These are project concepts related to the course subjects. Confirm the specific lessons you studied before describing the exact course content in a presentation.

## 4. Problem statement

Students revising lecture notes may reread material without identifying which concepts they misunderstand. Manually creating questions and checking answers takes time, and a generic quiz may not target the student's mistakes. The project addresses this problem for short, text-based study notes by providing immediate practice and a bounded feedback loop.

Scope: one student session, short pasted notes, multiple-choice assessment, source-linked feedback, and a maximum of three rounds. The project does not claim to replace a teacher or accurately measure long-term learning.

## 5. Proposed solution

**Project title:** StudyBuddy — Adaptive AI Learning Assistant.

The student provides notes and practice preferences. The model selects a quiz or asks a clarification question if the notes lack useful context. After deterministic scoring, the model chooses an explanation, a worked example, or a simpler explanation for missed concepts. Each concept receives a fresh explanation, an example, extra insight, and a self-check question. After observing the teaching result, the agent can recommend another quiz with selected difficulty and question style, or recommend finishing. The student can accept or end further practice.

### Agent and tool roles

| Component | Role and justification |
|---|---|
| Tutoring agent | Observes current state and tool results, chooses an allowed action and arguments, then observes what the executed tool returned. |
| Source preparation and retrieval | Labels note sections and prioritises sections matching weak topics. This is small and local, so lexical search is sufficient. |
| Validation gate | Checks the schema, four distinct self-contained options, question count, similar question text, source IDs, and source-text integrity. It prevents malformed output from reaching the quiz. |
| Answer-key scoring tool | Compares selected option indices with correct indices. A deterministic calculation avoids unnecessary LLM grading variation. |
| Teaching tools | Generate fresh concept explanations, worked examples, or simpler analogies according to the model-selected method. Add relevant background and self-check questions. |
| Clarification tool | Pauses for a specific question selected by the model and adds the student's answer to the context. |
| LangGraph executor | Validates and executes the selected action, stores observations, pauses for human input, and enforces bounds. |

The complete graph appears in the README and in `docs/diagrams/workflow.mmd`. The execution trace is recorded in the verification artifacts rather than displayed in the student interface.

## 6. Implementation

| Required field | Implementation |
|---|---|
| Programming language | Python 3.12 |
| LLM / AI model | GPT-OSS 20B via Groq (`openai/gpt-oss-20b`); optional original local model: Qwen 2.5 7B Instruct via LM Studio |
| Agent framework | LangGraph 1.2.16 |
| Tools / APIs | Groq OpenAI-compatible HTTP API; JSON Schema tool-selection protocol; teaching and quiz tools; deterministic retrieval, validation, and scoring; Pydantic schemas |
| Database / storage | In-memory LangGraph checkpointer and Streamlit session state; downloadable Markdown and JSON evidence; no database |
| Frontend | Streamlit 1.66.0 |
| Backend | Python functions in the Streamlit process with Groq-hosted inference |

### Implementation steps

1. Define the notes-to-practice problem and a small feature scope.
2. Create a schema for lessons and questions, including correct indices and source quotes.
3. Build the local model adapter using structured JSON output.
4. Prepare labelled note sections and retrieve relevant sections for revision.
5. Implement the observe–select–execute–observe loop with a tool catalogue, argument validation, and decision logging.
6. Add interrupts for answers and clarification, deterministic scoring, and model-directed teaching choices.
7. Generate expanded teaching cards and let the agent choose the next practice difficulty and style, with a student pause before another quiz.
8. Build the Streamlit interface, progress view, study-summary download, and separate technical evidence exports.
9. Test normal paths, error paths, and actual local-model generation.

### Generation controls

Notes are treated as study data rather than instructions. The model selects a source ID for each question, and the application copies that section's original text as evidence. The model does not generate the displayed quotation. The validation gate checks the source and quiz structure. Invalid structured output can be regenerated once. If the second attempt is invalid, or the server is unavailable, the application shows an error. It never silently substitutes sample questions for a live-model request.

Teaching can use established background knowledge beyond the notes and is labelled as additional tutor guidance. It must not be represented as verified source content. Original notes are available separately in a collapsed reference. Assessment questions remain based on the notes. Every missed concept must receive teaching before another quiz or completion, including when the overall score reaches the goal. There are at most three quizzes, two clarification questions, 24 agent decisions, and bounded repair attempts. A model-selected finish below the goal is not labelled as passing.

## 7. Testing and evidence

See `docs/testing-evidence.md` for the matrix and actual evidence files. Tests verify that different model-selected teaching tools execute at the same score, agent-selected difficulty reaches quiz generation, an agent can offer more practice after a perfect score, and an agent can finish below the goal without inventing mastery. Other tests cover feedback for missed concepts at the target boundary, copied-note rejection, clarification, invalid actions, saved results after failure, scoring, bounds, and the interface journey.

The live verification script calls the configured model for action selection, quiz generation, and expanded teaching. It deliberately submits wrong answers to exercise feedback and accepts a model-recommended follow-up quiz with scripted correct answers. The Groq run completed with three generated teaching cards and scores of 0% and 100%; its actual decisions and outputs are saved separately in `artifacts/groq-live-verification/`. The earlier Qwen evidence is also retained. This checks software behaviour; it does not demonstrate learning improvement or independently establish factual correctness. Public hosting still needs its own verification.

## 8. Final project demonstration

**Prototype / application link:** Local prototype: http://127.0.0.1:8501. This address works only on the machine running StudyBuddy. Add the final deployment link after deployment.

**GitHub repository:** https://github.com/shanvsrivas/Flexi-AgenticAI

**Demonstration:** Show notes, the generated quiz, source-linked feedback, a follow-up round, progress history, and the graph trace. Use `docs/demo-and-viva.md` for a short script. Label sample mode if it is used.

## 9. Individual reflection — complete in your own words

Use these prompts rather than submitting invented first-person claims:

- Which parts of the code can you explain without reading a script?
- Why is answer-key scoring a Python function rather than an LLM call?
- Which result or error did you observe, and what did it reveal?
- How do `interrupt`, `Command`, and the thread ID work together?
- What trade-off did lexical retrieval make compared with a vector database?
- What did you implement or change yourself, and where did you use AI assistance?

## 10. Limitations and conclusion

StudyBuddy demonstrates a small, working agentic learning workflow using a local model, tools, shared graph state, human input, and feedback. Its bounded scope makes the decisions visible and testable.

The model can generate incorrect questions, answer keys, extra facts, or unhelpful teaching decisions. Quote matching establishes source presence, not factual correctness or logical support; extra teaching is not independently fact-checked. Retrieval is lexical and similar questions can recur. Multiple agent and teaching calls take longer than a single quiz-generation request. Scores are session-specific, not a validated mastery measure. In-memory checkpoints do not survive application restarts.

Future improvements could include persistent checkpoints, file uploads, teacher-reviewed question banks, stronger checks for answer support, and improved retrieval. These features are not claimed as implemented.

## References and assistance

- LangGraph documentation: https://docs.langchain.com/oss/python/langgraph/
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- LM Studio local server: https://lmstudio.ai/docs/developer/core/server
- LM Studio structured output: https://lmstudio.ai/docs/developer/openai-compat/structured-output

Development used AI coding assistance. Review the code and report, accurately describe your own contributions, and follow the course's disclosure requirements.
