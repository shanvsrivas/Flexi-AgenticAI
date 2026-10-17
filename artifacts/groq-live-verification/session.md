Verification method: scripted answers exercise the workflow; scores do not measure student learning.

# StudyBuddy — session evidence

Date: 2026-10-17T12:59:46.771141+05:30
Mode: live
Model: openai/gpt-oss-20b
Status: mastered
Session target: 80%

This is an automatically recorded practice session, not a claim of general learning mastery.

## Round 1

Score: 0/3 (0.0%)
Weak topics: AI agents, LangGraph state, Conditional edges

### 1. Which statement best describes an AI agent?

Selected: It is a static rule-based system that never changes its behavior.
Correct: It observes information, decides actions, and uses tools to achieve a goal.
Result: Incorrect
Explanation: An AI agent observes information, decides what to do, and takes actions using tools to work toward a goal, combining a language model with a control loop.
Source: S01
> AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

### 2. What role does LangGraph state play in a workflow?

Selected: It replaces the need for conditional edges.
Correct: It stores shared information that nodes read and update.
Result: Incorrect
Explanation: LangGraph state holds shared information such as notes, questions, answers, scores, and weak topics that nodes can read and modify during execution.
Source: S02
> LangGraph state
State is shared information passed between graph nodes. It can store the student's notes, generated questions, answers, scores, and weak topics. A node reads the current state and returns updates to it.

### 3. In a quiz scenario, what happens when a student scores 75%?

Selected: The student receives a congratulatory message.
Correct: The student is routed to revision.
Result: Incorrect
Explanation: A conditional edge routes the next node based on the current state; a score below 80% directs the student to revision, while 80% or higher would finish the session.
Source: S03
> Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

### Concepts to revisit

Tutor explanations include background information beyond the supplied notes.

#### AI agents

You might think an AI agent only writes text and never makes decisions or uses tools.

A true AI agent watches the environment, decides what to do next, and then acts—often by calling external tools—so it can reach a goal. It’s not just a language model that spits out sentences; it’s a loop that observes, plans, and executes.

Example: Imagine a tutoring bot that sees a student’s low quiz score, decides to offer extra practice, and then calls a math solver tool to generate new problems. The bot’s actions are guided by its observations and a goal of improving learning.

Extra insight: The control loop lets the agent react to changing states, unlike a static script. This dynamic behavior is what distinguishes agents from simple models.

Self-check: How does an AI agent’s use of a control loop and tools enable it to adapt to a student’s needs?

#### LangGraph state

Some think state is only for final output or logging, not for ongoing data sharing.

In LangGraph, state is a shared data store that nodes read from and write to as the workflow runs. It holds notes, questions, answers, scores, and weak topics, allowing later nodes to build on earlier work.

Example: During a lesson, a node records a student’s answer and updates the score in state. A later node reads that score to decide whether to give feedback or move on, all using the same state object.

Extra insight: Because state is mutable, it can capture the evolving context of a conversation, making the graph behave like a stateful program rather than a sequence of isolated steps.

Self-check: Why is it important that LangGraph state is shared and mutable across nodes?

#### Conditional edges

You might think all edges in a graph behave the same, always leading to the same next node.

Conditional edges examine the current state and choose the next node based on conditions, such as a quiz score. They allow the workflow to branch dynamically instead of following a fixed path.

Example: If a student scores 75% on a quiz, a conditional edge routes them to a revision node. If they score 85%, the edge sends them to a completion node, demonstrating different paths from the same starting point.

Extra insight: Conditional edges make the graph responsive to real-time data, turning a linear flow into a decision tree that adapts to user performance.

Self-check: How does a conditional edge change the flow of a graph compared to a normal edge?

## Round 2

Score: 3/3 (100.0%)
Weak topics: None in this quiz

### 1. Which of the following best describes the primary function of an AI agent?

Selected: It observes information, decides actions, and uses tools to achieve a goal.
Correct: It observes information, decides actions, and uses tools to achieve a goal.
Result: Correct
Explanation: An AI agent observes information, decides what to do, and takes actions using tools to work toward a goal, combining a language model with a control loop and tools.
Source: S01
> AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

### 2. What type of information is typically stored in LangGraph state during a quiz workflow?

Selected: Shared data such as notes, scores, and weak topics between nodes.
Correct: Shared data such as notes, scores, and weak topics between nodes.
Result: Correct
Explanation: LangGraph state holds shared information passed between graph nodes, including the student's notes, generated questions, answers, scores, and weak topics.
Source: S02
> LangGraph state
State is shared information passed between graph nodes. It can store the student's notes, generated questions, answers, scores, and weak topics. A node reads the current state and returns updates to it.

### 3. In a quiz scenario, what happens when a student's score is below 80 percent?

Selected: The student is routed to a revision node via a conditional edge.
Correct: The student is routed to a revision node via a conditional edge.
Result: Correct
Explanation: A conditional edge chooses the next node based on the current state; a score below 80 percent routes the student to a revision node, while a score of at least 80 percent can finish the session.
Source: S03
> Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

## Agent-selected actions

- Round 1 · create_quiz (Standard, recall): The student has prepared notes covering key concepts. A standard recall quiz will assess understanding of these topics and help identify weak areas before moving to application questions.
- Round 1 · explain_concept (Standard, recall): All three student answers were incorrect, indicating conceptual misunderstandings. An explain_concept action will clarify each topic, compare the mistaken and correct statements, and provide background to solidify understanding.
- Round 1 · create_quiz (Standard, recall): The student struggled with basic recall of key concepts after the explanations. A standard recall quiz will reinforce understanding and identify remaining weak areas.
- Round 2 · create_quiz (Standard, recall): The student struggled with all three topics; a new quiz will assess recall and guide further revision.
- Round 2 · finish (Standard, recall): The student achieved a perfect score on the quiz, meeting the score goal. No further practice is needed.
## Workflow trace

- Round 1 · prepare_notes: Prepared 5 labelled source sections.
- Round 1 · select_action: Selected create_quiz: The student has prepared notes covering key concepts. A standard recall quiz will assess understanding of these topics and help identify weak areas before moving to application questions.
- Round 1 · create_quiz: Executed selected quiz tool: Standard, recall; 4 source sections.
- Round 1 · validate_quiz: Schema, options, sources, and question checks passed.
- Round 1 · await_answers: Student submitted every answer; resumed the saved graph.
- Round 1 · grade_answers: Answer-key scoring: 0/3 = 0.0%.
- Round 1 · select_action: Selected explain_concept: All three student answers were incorrect, indicating conceptual misunderstandings. An explain_concept action will clarify each topic, compare the mistaken and correct statements, and provide background to solidify understanding.
- Round 1 · explain_concept: Executed model-selected teaching tool for: AI agents, LangGraph state, Conditional edges
- Round 1 · select_action: Selected create_quiz: The student struggled with basic recall of key concepts after the explanations. A standard recall quiz will reinforce understanding and identify remaining weak areas.
- Round 1 · await_revision: Student chose retry.
- Round 2 · create_quiz: Executed selected quiz tool: Standard, recall; 4 source sections.
- Round 2 · validate_quiz: Quiz held back: questions.0.options: List should have at most 4 items after validation, not 5; questions.1.options: List should have at most 4 items after validation, not 5; questions.2.options: List should have at most 4 items after validation, not 5
- Round 2 · select_action: Selected create_quiz: The student struggled with all three topics; a new quiz will assess recall and guide further revision.
- Round 2 · create_quiz: Executed selected quiz tool: Standard, recall; 4 source sections.
- Round 2 · validate_quiz: Schema, options, sources, and question checks passed.
- Round 2 · await_answers: Student submitted every answer; resumed the saved graph.
- Round 2 · grade_answers: Answer-key scoring: 3/3 = 100.0%.
- Round 2 · select_action: Selected finish: The student achieved a perfect score on the quiz, meeting the score goal. No further practice is needed.
- Round 2 · finish: Agent recommended finishing: The student achieved a perfect score on the quiz, meeting the score goal. No further practice is needed.

## Source notes

### S01

AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

### S02

LangGraph state
State is shared information passed between graph nodes. It can store the student's notes, generated questions, answers, scores, and weak topics. A node reads the current state and returns updates to it.

### S03

Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

### S04

Tools and reliable scoring
A tool is a function that an agent workflow can use to perform a specific task, such as retrieving notes or calculating a quiz score. For multiple-choice questions, comparing selected option indices with an answer key gives deterministic scoring without another LLM call.

### S05

Checkpoints and human input
A checkpointer saves graph state at execution steps. An interrupt pauses a graph until the student provides input. Resuming with Command and the same thread ID lets the workflow continue from its saved checkpoint. In-memory checkpoints are lost when the application process restarts.
