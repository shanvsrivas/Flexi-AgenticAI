"""Fixed fixtures for offline demonstrations. These are NOT AI-generated at runtime."""

from copy import deepcopy

SAMPLE_NOTES = """AI agents
An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal. A language model produces text; an agent combines a model with a control loop and tools.

LangGraph state
State is shared information passed between graph nodes. It can store the student's notes, generated questions, answers, scores, and weak topics. A node reads the current state and returns updates to it.

Conditional edges
A normal edge always leads to the same next node. A conditional edge chooses the next node based on the current state. In a quiz, a score below 80 percent can route to revision, while a score of at least 80 percent can finish the session.

Tools and reliable scoring
A tool is a function that an agent workflow can use to perform a specific task, such as retrieving notes or calculating a quiz score. For multiple-choice questions, comparing selected option indices with an answer key gives deterministic scoring without another LLM call.

Checkpoints and human input
A checkpointer saves graph state at execution steps. An interrupt pauses a graph until the student provides input. Resuming with Command and the same thread ID lets the workflow continue from its saved checkpoint. In-memory checkpoints are lost when the application process restarts.
"""

_ITEMS = [
    ("AI agents", "What distinguishes the agent described in these notes from a text-only model?", ["It only stores documents", "It combines a model, tools, and a control loop", "It never observes information", "It must use several models"], 1, "An AI agent uses observations, decisions, and tools to work towards a goal.", "S01", "An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal."),
    ("LangGraph state", "Where should the student's answers and weak topics be kept between nodes?", ["Only inside a button label", "In the model name", "In the shared graph state", "Inside a CSS file"], 2, "State carries shared information, including answers and weak topics, between graph nodes.", "S02", "State is shared information passed between graph nodes."),
    ("Conditional edges", "Which graph feature sends a low-scoring student to revision?", ["A conditional edge", "A fixed page title", "A model download", "A normal edge with no decision"], 0, "A conditional edge chooses a route based on state, such as the latest score.", "S03", "A conditional edge chooses the next node based on the current state."),
    ("Tools and reliable scoring", "How can multiple-choice answers be scored reproducibly?", ["Ask the model to guess a mark", "Choose a random score", "Count the words in the answer", "Compare selected option indices with an answer key"], 3, "The same answer key and submitted indices always give the same score.", "S04", "comparing selected option indices with an answer key gives deterministic scoring without another LLM call."),
    ("Checkpoints and human input", "What is needed to continue a paused graph from its saved checkpoint?", ["A new thread ID every time", "Command and the same thread ID", "A different model every time", "Deleting the saved state"], 1, "Resume the interrupt using Command with the same thread ID to continue the saved session.", "S05", "Resuming with Command and the same thread ID lets the workflow continue from its saved checkpoint."),
    ("AI agents", "Which action best matches the definition of an AI agent in the notes?", ["Saving a static heading", "Displaying text without a goal", "Observing a request and choosing a tool to pursue a goal", "Removing every tool from a workflow"], 2, "Agents combine observations, decisions, and actions to pursue a goal.", "S01", "An AI agent observes information, decides what to do, and takes actions using tools to work towards a goal."),
    ("LangGraph state", "What does a graph node return after reading the current state?", ["Updates to the state", "Only a stylesheet", "A model download", "Always a new application"], 0, "A node receives the current state and returns updates for following nodes.", "S02", "A node reads the current state and returns updates to it."),
    ("Conditional edges", "Using the rule in these notes, where should a score of exactly 80 percent route?", ["Back to uploading notes", "To an error", "Always to revision", "To finish the session"], 3, "The rule uses at least 80 percent, so the boundary score finishes the session.", "S03", "a score of at least 80 percent can finish the session."),
    ("Tools and reliable scoring", "Which is an example of a tool in this workflow?", ["The color of the background", "A function that retrieves notes", "The student's name alone", "A decorative border"], 1, "Tools perform tasks such as source retrieval and score calculation.", "S04", "A tool is a function that an agent workflow can use to perform a specific task, such as retrieving notes or calculating a quiz score."),
    ("Checkpoints and human input", "What happens to in-memory checkpoints when the app process restarts?", ["They are lost", "They become permanent files", "They are emailed to the teacher", "They train the model"], 0, "The in-memory checkpointer lasts only while the application process is running.", "S05", "In-memory checkpoints are lost when the application process restarts."),
]


class SampleTutor:
    mode = "sample"
    model = "Fixed sample fixture (no LLM)"

    def decide(self, context, feedback):
        allowed = {tool["name"] for tool in context["allowed_tools"]}
        scores = context["score_history"]
        if "explain_concept" in allowed:
            tool, topics = "explain_concept", context["unreviewed_topics"]
        elif "finish" in allowed and (scores[-1]["score"] >= context["score_goal"] or "create_quiz" not in allowed):
            tool, topics = "finish", []
        else:
            tool, topics = "create_quiz", context["unreviewed_topics"]
        return {"tool": tool, "topics": topics, "difficulty": "Foundation" if scores and scores[-1]["score"] < 60 else context["requested_difficulty"], "question_style": "application" if scores else "recall", "reason": "Preset demonstration: review missed concepts, then practise again or finish.", "question": ""}

    def teach(self, *, chunks, mistakes, topics, method, feedback):
        material = {
            "AI agents": (
                "An agent connects a goal to actions: it observes what happened, chooses a useful next step, and uses the result to decide again. Generating a sentence alone does not provide that action loop.",
                "Imagine a tutor seeing a wrong quiz answer. It chooses an example, reads the student's next answer, and decides whether another question would help.",
                "Agent autonomy can be bounded: permitted tools and time limits can be enforced while the agent still chooses among the available actions.",
                "What observation would make a tutoring agent change its next action?"),
            "LangGraph state": (
                "Think of state as a shared notebook for the whole session. One step writes the student's answer, another adds a score, and the next reads both to choose useful feedback. It is not private storage for a single node.",
                "After a student chooses option B, the scoring step adds 66.7% to the notebook. The tutor can then read both the answer and score without asking the student to enter them again.",
                "Session state changes the information supplied to the tutor. It does not retrain the language model or change the model's weights.",
                "Why would the revision step need access to both your answer and the correct answer?"),
            "Conditional edges": (
                "A conditional edge acts like a junction: it examines a value in state and selects the next path. The value can be a score or the tool chosen by a model, so the graph can support either rules or agent decisions.",
                "If a tutor selects worked_example, the graph runs the example tool. If it selects finish, the graph ends the session instead of creating another quiz.",
                "The existence of a branch alone does not make a system autonomous. What matters is whether a model chooses a meaningful action or every action is fixed by a rule.",
                "How could the same graph route to an explanation in one session and an example in another?"),
            "Tools and reliable scoring": (
                "A tool performs a concrete operation for the tutor. For a multiple-choice quiz, a scoring tool compares each chosen option with the stored key and counts the matches, rather than guessing a percentage.",
                "Three matching answers out of five gives 3 divided by 5 times 100, or 60%. Repeating that calculation with the same choices gives the same result.",
                "Reproducible scoring does not guarantee the generated answer key is factually correct. A teacher can review the key while the calculation remains deterministic.",
                "Which part needs factual review: the percentage calculation or the generated answer key?"),
            "Checkpoints and human input": (
                "A checkpoint is a bookmark for the workflow. An interrupt waits at that bookmark for the student, and resuming with the same thread ID continues the saved session instead of starting a different one.",
                "The tutor shows a quiz and pauses. When you submit the answers, Command carries them back to that waiting workflow so the scoring tool can run.",
                "An in-memory bookmark survives ordinary steps within the running process, but durable storage would be needed to retain it through a server restart.",
                "Why should a resumed quiz use the same thread ID?"),
        }
        cards = []
        for topic in topics:
            item = next(m for m in mistakes if m["topic"] == topic)
            explanation, example, extra, check = material[topic]
            cards.append({"topic": topic, "misconception": f"A common mix-up is choosing '{item['options'][item['selected_index']]}' instead of '{item['options'][item['correct_index']]}'.", "explanation": explanation, "example": example, "extra_info": extra, "check_question": check, "source_id": item["source_id"]})
        return {"cards": cards}

    def generate(self, *, chunks, count, difficulty, round_number, weak_topics, previous_questions, feedback, question_style="recall"):
        bank = _ITEMS[:5] if round_number == 1 else _ITEMS[5:]
        # Prioritise mistakes, then fill with remaining concepts for a full quiz.
        bank = sorted(bank, key=lambda item: item[0] not in weak_topics)
        questions = [dict(zip(["topic", "question", "options", "correct_index", "explanation", "source_id", "evidence"], item)) for item in bank[:count]]
        return deepcopy({
            "title": "AI agents & LangGraph fundamentals",
            "overview": "Understand how agents use tools, how LangGraph moves state between nodes, and how a quiz can adapt to a student's answers.",
            "takeaways": ["Agents combine models, a control loop, and tools.", "State connects nodes; conditional edges choose a route.", "Interrupts pause a graph until the student responds."],
            "strategy": "Revisit missed topics first, then check understanding with another sample question." if weak_topics else "Begin with a broad check across the core concepts in the sample notes.",
            "questions": questions,
        })
