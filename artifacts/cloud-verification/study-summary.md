Cloud verification: scripted answers test the software, not student learning.

# Your StudyBuddy summary

Date: 2026-10-17
Score goal: 80%

## Round 1

Score: 0/3 (0.0%)
Weak topics: AI agents, Conditional edges, Checkpoints and human input

### 1. Which component is NOT part of an AI agent’s core architecture?

Selected: Language model
Correct: Database server
Result: Incorrect
Explanation: An AI agent uses a language model, a control loop, and tools to act on goals; a database server is not part of the core architecture.
From your notes:
> AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

### 2. In a quiz workflow, a score below 80% will most likely route the student to which node?

Selected: Finish the session
Correct: Revision
Result: Incorrect
Explanation: Conditional edges use the current state; a score below 80% directs the workflow to a revision node.
From your notes:
> Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

### 3. What happens to an in‑memory checkpoint if the application process restarts?

Selected: It is automatically restored
Correct: It is lost
Result: Incorrect
Explanation: In‑memory checkpoints are lost when the application process restarts.
From your notes:
> Checkpoints and human input
A checkpointer saves graph state at execution steps. An interrupt pauses a graph until the student provides input. Resuming with Command and the same thread ID lets the workflow continue from its saved checkpoint. In-memory checkpoints are lost when the application process restarts.

### Concepts to revisit

Tutor explanations include background information beyond the supplied notes.

#### AI agents

You might think a database server is a core part of an AI agent’s architecture.

A core AI agent consists of a language model that generates text, a control loop that decides what to do next, and tools that perform concrete actions. The agent’s logic is built around these three components; a database server is external storage and not part of the agent’s essential loop.

Example: Imagine a cooking assistant: the language model suggests recipes, the control loop chooses the next step (e.g., chop, sauté), and the tool is a kitchen appliance that actually chops. A separate pantry database stores ingredients but isn’t part of the agent’s core decision‑making.

Extra insight: While agents can read from or write to databases, the database itself is not a required building block; it’s just another tool or data source the agent can use.

Self-check: What are the three core components that make up an AI agent’s architecture?

#### Conditional edges

You might think a low quiz score always leads to finishing the session.

Conditional edges choose the next node based on the current state. In a quiz, if the student’s score is below 80 %, the workflow routes to a revision node so the student can review material. Only scores of 80 % or higher trigger the finish node.

Example: A student answers 7 out of 10 questions correctly (70 %). The state holds this score; the conditional edge reads it and sends the student to a ‘Review Topics’ node instead of ‘End Session.’

Extra insight: Conditional edges allow dynamic branching, enabling personalized learning paths rather than a single linear flow.

Self-check: In a quiz workflow, what node does a score below 80 % route the student to?

#### Checkpoints and human input

You might think in‑memory checkpoints survive an application restart.

A checkpointer saves the graph state at execution steps. When the application process restarts, any checkpoints stored only in memory are lost; they are not persisted to disk automatically.

Example: During a lesson, the system pauses for a student’s input and saves the state in memory. If the server crashes and restarts, that saved state disappears, so the workflow must start over or recover from a persisted checkpoint.

Extra insight: To preserve state across restarts, checkpoints must be written to durable storage (e.g., a database or file).

Self-check: What happens to an in‑memory checkpoint if the application process restarts?
