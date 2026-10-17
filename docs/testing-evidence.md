# Testing evidence

## Recorded verification

- **Current combined suite: 61 tests passed**, including Groq credentials/protocol, provider-side schema repair, short rate-limit retries, and the complete Streamlit interface journey. Result: `artifacts/test-results/groq-tests.xml`. The earlier 48-test result remains in `artifacts/test-results/test-results.xml`.
- **Live Groq flow passed** with `openai/gpt-oss-20b`: quiz, scripted wrong answers (0%), three generated teaching cards, focused follow-up quiz, scripted correct answers (100%), and `finish`. Final status: `mastered`. Evidence: `artifacts/groq-live-verification/session.json` and `session.md`. Short free-tier token limits occurred and were handled by a bounded wait/retry. This verifies live inference locally; public hosting must be checked separately.
- The original local Qwen run is retained in `artifacts/live-verification/session.json` and `session.md`; it is separate from the current Groq evidence.
- Live answers are scripted to exercise decisions, not to represent a student. The agent can offer more practice after reaching the goal or recommend finishing below it; the script records those choices honestly.

The completed live agent run passed: Qwen selected `create_quiz`, then three `explain_concept` actions for missed concepts, then `create_quiz` with application questions, then `finish`. The scripted scores were 0% and 100%. Three expanded teaching cards and their original source references are retained in `teaching_history`. This demonstrates actual model-selected actions and feedback, not an evaluation of student learning or a guarantee that every explanation is correct.

The live script submits answers programmatically to exercise routes. The recorded 0% and 100% are not a student's marks or evidence of learning improvement. Automated fixture tests are separate from actual live generation.

## Test matrix

| Case | Input / action | Expected behaviour | Recorded result and interpretation |
|---|---|---|---|
| Valid notes | Sample subject notes; 3–5 questions | Generate a validated quiz and pause | Passed. Actual LangGraph waits at `await_answers`. |
| Exact target with a mistake | 4 correct out of 5; 80% target | Teach the missed concept before continuing or finishing | Passed. Sample tutor finishes with a teaching card; live agent may recommend more practice. |
| Below target | 3 correct out of 5 | Expose actual mistakes to the agent and execute its teaching selection | Passed. Score is 60%; next action comes from the selected tool rather than a score-routing table. |
| No correct answers | All selected indices intentionally wrong | Score 0%; revise | Passed in fixtures and the live model run. |
| Adaptive follow-up | Retry after mistakes | Preserve history, increment round, provide weak-topic context | Passed. Fixture test checks topic priority; live output shows follow-up topics and new question text. Semantic distinctness is not guaranteed. |
| Round bound | Fail three consecutive quizzes | Stop after round three | Passed. No unbounded practice loop. |
| Student stops | Choose Finish for now after revision | End without inventing a passing result | Passed. Status becomes `finished`. |
| Incomplete answers | Empty selection or a missing answer | Reject without advancing state | Passed. The original quiz checkpoint remains available. |
| Invalid indices | Boolean, text, or index outside 0–3 | Reject | Passed. Inputs do not create a score. |
| Ambiguous option style | An option says Both A and B | Reject | Passed. Options must be self-contained. |
| Near-identical follow-up | A previous question with only slight wording changes | Reject | Passed using text similarity. This does not establish semantic novelty for every question. |
| Repeated submission | Submit a completed quiz again | Reject, preserve one result | Passed. No duplicate history entry. |
| Too-short / oversized notes | Fewer than 100 chars/20 words or over 10,000 chars | Reject before generation | Passed. Clear validation error. |
| Invented quote | Quote absent from indicated source | Hold quiz back; attempt one repair | Passed. No invalid quiz is displayed. |
| Failed repair | Invalid output twice | Stop with generation error | Passed. Exactly two generation attempts. |
| Successful repair | Invalid quote followed by valid quote | Present only the repaired quiz | Passed. Source validation succeeds before interruption. |
| Model unavailable | Simulated server failure | Show error, no sample fallback | Passed. No fixture content substituted. |
| Session separation | Two different graph thread IDs | Separate source and question state | Passed. Checkpoints remain isolated. |
| Local API adapter | Mock HTTP response | Send JSON schema, parse response, attach original source text | Passed. Source evidence is copied by the application; no OpenAI cloud call is required. |
| Evidence export | Download generated results | Include scores, sources, mode, and trace | Passed. Connection credentials excluded. |
| Interface journey | Start sample, submit incomplete, submit mistakes, retry, pass, reset | Correct controls and transitions | Passed using Streamlit AppTest. |
| Same score, different action | Model stand-in selects explanation, worked example, or simplification at 0% | Execute that selected tool | Passed for all three methods. This tests model control of action selection. |
| Difficulty and style choice | Agent chooses Foundation/application | Forward choices into the next quiz tool | Passed. Fixed score thresholds do not override those arguments. |
| Continue after perfect score | Agent chooses a Challenge application quiz at 100% | Offer the chosen practice rather than force completion | Passed. Student still chooses whether to take it. |
| Finish below target | Agent chooses finish after teaching at 0% | End without claiming mastery | Passed. Result remains 0%; status is finished, not mastered. |
| Skip-feedback attempt | Model attempts to finish before reviewing mistakes | Reject selection | Passed. No illegal tool executes; scored answers survive. |
| Copied-note explanation | Teaching tool repeats source text verbatim | Retry, then reject if unchanged | Passed. No copied-note fallback is presented as personalised teaching. |
| Clarification | Agent asks for context, student responds | Pause, validate input, add context, resume agent | Passed. Invalid empty input leaves the checkpoint unchanged. |
| Invalid action | Malformed or unsupported tool selection | Reject without running generation | Passed. The model cannot invoke an arbitrary operation. |
| Feedback persistence | Complete another quiz after teaching | Retain earlier explanations in exports | Passed. Teaching history and action history are preserved. |
| Failed follow-up | Second quiz generation fails | Preserve the last valid quiz and scored answers | Passed. Failure does not erase progress. |

## Interpretation and remaining checks

These checks verify routing, calculations, validation, and a local-model integration. They do not establish educational effectiveness, factual correctness for all notes, robustness against every prompt injection, or performance under multiple users.

Manual reviews have found imprecise answer options, overconfident extra explanations, and near-repeated questions in local-model trials. Prompts and repair feedback were tightened, but extra information and answer-key correctness are not independently fact-checked. Structural validation does not guarantee semantic correctness.

Earlier trials also exposed ambiguous "Both A and B" options and unreliable model-copied quotations. The application rejects referential options and attaches original source text using the selected source ID. Failed live runs remain failures; the verification script exits with an error when generation or feedback fails, rather than claiming success.

Browser screenshots: `artifacts/screenshots/01-home.png` shows the local application; `artifacts/screenshots/02-sample-revision.png` shows feedback from an explicitly labelled sample session. The latter is UI evidence, not live model generation evidence.

`artifacts/screenshots/05-expanded-concept-teaching.png` shows the upgraded explanation, example, and extra-insight layout using the labelled preset example session. Real Qwen decisions and generated explanations are recorded separately in the live-verification files.

Before presenting, manually read each generated question and answer key. Add screenshots from your own demo and any further subjects you test. Do not label fixture output as live AI output. Keep `session.json` unchanged as the record of the actual local-model run.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/test-results/test-results.xml
.\.venv\Scripts\python.exe scripts/live_smoke.py
```

The second command uses the configured provider: Groq by default, or LM Studio when explicitly selected. It needs a real connection and replaces the saved live verification files with the new actual run. The retained Qwen artifacts are historical evidence; the Groq verification was saved separately in `artifacts/groq-live-verification/`. Automated provider tests use mocks, while those live Groq artifacts record actual inference.
