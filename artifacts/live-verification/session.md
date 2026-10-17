Verification method: answers were scripted to exercise routing. These scores do not represent a student's learning gain.

# StudyBuddy — session evidence

Date: 2026-10-17T04:45:30.684087+05:30
Mode: live
Model: qwen2.5-7b-instruct
Status: mastered
Session target: 80%

This is an automatically recorded practice session, not a claim of general learning mastery.

## Round 1

Score: 0/3 (0.0%)
Weak topics: AI Agents, LangGraph State, Conditional Edges

### 1. What does an AI agent do when it observes information?

Selected: It ignores the information and continues with its current task.
Correct: It decides what actions to take based on the observed information.
Result: Incorrect
Explanation: An AI agent observes information, decides what to do, and takes actions using tools.
Source: S01
> AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

### 2. Which of the following is NOT a component that can be stored in LangGraph state?

Selected: Generated questions
Correct: AI agent code
Result: Incorrect
Explanation: LangGraph state can store student's notes, generated questions, answers, scores, and weak topics.
Source: S02
> LangGraph state
State is shared information passed between graph nodes. It can store the student's notes, generated questions, answers, scores, and weak topics. A node reads the current state and returns updates to it.

### 3. In a quiz scenario using conditional edges, what action is taken if the score is below 80 percent?

Selected: The session ends immediately.
Correct: The next node is a revision section.
Result: Incorrect
Explanation: A score below 80 percent can route to a revision section.
Source: S03
> Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

### Concepts to revisit

Tutor explanations include background information beyond the supplied notes.

#### AI Agents

A common mix-up is that an AI agent simply stores the observed information without processing it.

An AI agent observes information, decides what to do, and takes actions using tools. The key point here is that the agent makes decisions based on the observed data, not just storing it for later use.

Example: Imagine an AI assistant observing your calendar entries. It doesn't merely save these entries; instead, it uses them to remind you of upcoming meetings or suggest scheduling changes.

Extra insight: While storage is part of how an AI agent operates, the primary function is decision-making and action-taking based on observed information.

Self-check: What does an AI agent do with observed data besides storing it?

#### LangGraph State

The student might think that AI agent code can be stored in LangGraph state.

LangGraph state is designed to store shared information like the student's notes, generated questions, answers, scores, and weak topics. It does not include executable code such as an AI agent. The state primarily holds data relevant for the graph nodes' operations, not full program logic or agents.

Example: Imagine a LangGraph where each node represents a quiz question. The state would store the student's answers to these questions, their scores, and any notes they took during the session. However, it wouldn't contain the code that generates new questions or evaluates them; those are separate processes.

Extra insight: While the state can hold various data types, it is not meant for storing executable scripts or full-fledged AI agents. These would be part of the application logic outside the LangGraph's state management.

Self-check: What type of information should NOT be stored in LangGraph state according to the passage?

#### Conditional Edges

A common mix-up is thinking that a score below 80 percent ends the session immediately.

In a quiz scenario using conditional edges, if the score is below 80 percent, it does not end the session. Instead, a conditional edge allows the system to route the student to a revision section where they can review material before potentially retaking the quiz or finishing the session with additional preparation.

Example: Imagine you're taking an online math test. If your score is below 80 percent, instead of ending the test, it might automatically direct you to a set of practice problems related to the topics you struggled with.

Extra insight: This routing ensures that students can address their weaknesses before moving on, which can improve overall understanding and performance.

Self-check: What happens if your score is below 80 percent in this quiz?

## Round 2

Score: 3/3 (100.0%)
Weak topics: None in this quiz

### 1. An AI agent is given a task to help a student prepare for a math exam. Which of the following best describes what the agent does when it observes the student’s weak topics in LangGraph state?

Selected: It generates practice questions targeted at those weak areas.
Correct: It generates practice questions targeted at those weak areas.
Result: Correct
Explanation: The agent uses the observed weak topics in LangGraph state to generate relevant and targeted practice questions, helping the student improve in those areas.
Source: S01
> AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

### 2. During a quiz session, if a student's score is below 80 percent, which of the following actions will an AI agent take based on conditional edges?

Selected: It will route to a revision section where more practice questions are available.
Correct: It will route to a revision section where more practice questions are available.
Result: Correct
Explanation: The conditional edge will direct the flow of the quiz to a revision section, providing more practice questions before allowing the student to continue.
Source: S03
> Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

### 3. In a scenario where an AI agent is managing a quiz session, which statement best describes how conditional edges are used?

Selected: Conditional edges choose the next node based on the student's score in LangGraph state.
Correct: Conditional edges choose the next node based on the student's score in LangGraph state.
Result: Correct
Explanation: Conditional edges route to the next node based on the current state, such as directing students with low scores to revision sections.
Source: S03
> Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

## Agent-selected actions

- Round 1 · create_quiz (Standard, recall): Starting with recall questions on the introduced topics to assess basic understanding.
- Round 1 · explain_concept (Standard, recall): The student's answer is incorrect and needs a clear explanation of the concept.
- Round 1 · explain_concept (Standard, recall): The student incorrectly identified 'AI agent code' as a component of LangGraph state, indicating a need for further clarification on what can and cannot be stored in the state.
- Round 1 · explain_concept (Standard, recall): The student has not yet grasped the concept of conditional edges, as evidenced by their incorrect answer in the latest quiz.
- Round 1 · create_quiz (Standard, application): The student has shown conceptual confusion and difficulty applying knowledge, so creating a quiz with application questions will help reinforce the material.
- Round 2 · finish (Standard, recall): The student has achieved the score goal of 80% and all previous answers were correct. There are no unreviewed topics, so finishing is appropriate.
## Workflow trace

- Round 1 · prepare_notes: Prepared 5 labelled source sections.
- Round 1 · select_action: Selected create_quiz: Starting with recall questions on the introduced topics to assess basic understanding.
- Round 1 · create_quiz: Executed selected quiz tool: Standard, recall; 4 source sections.
- Round 1 · validate_quiz: Schema, options, sources, and question checks passed.
- Round 1 · await_answers: Student submitted every answer; resumed the saved graph.
- Round 1 · grade_answers: Answer-key scoring: 0/3 = 0.0%.
- Round 1 · select_action: Selected explain_concept: The student's answer is incorrect and needs a clear explanation of the concept.
- Round 1 · explain_concept: Executed model-selected teaching tool for: AI Agents
- Round 1 · select_action: Selected explain_concept: The student incorrectly identified 'AI agent code' as a component of LangGraph state, indicating a need for further clarification on what can and cannot be stored in the state.
- Round 1 · explain_concept: Executed model-selected teaching tool for: LangGraph State
- Round 1 · select_action: Selected explain_concept: The student has not yet grasped the concept of conditional edges, as evidenced by their incorrect answer in the latest quiz.
- Round 1 · explain_concept: Executed model-selected teaching tool for: Conditional Edges
- Round 1 · select_action: Selected create_quiz: The student has shown conceptual confusion and difficulty applying knowledge, so creating a quiz with application questions will help reinforce the material.
- Round 1 · await_revision: Student chose retry.
- Round 2 · create_quiz: Executed selected quiz tool: Standard, application; 4 source sections.
- Round 2 · validate_quiz: Schema, options, sources, and question checks passed.
- Round 2 · await_answers: Student submitted every answer; resumed the saved graph.
- Round 2 · grade_answers: Answer-key scoring: 3/3 = 100.0%.
- Round 2 · select_action: Selected finish: The student has achieved the score goal of 80% and all previous answers were correct. There are no unreviewed topics, so finishing is appropriate.
- Round 2 · finish: Agent recommended finishing: The student has achieved the score goal of 80% and all previous answers were correct. There are no unreviewed topics, so finishing is appropriate.

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
