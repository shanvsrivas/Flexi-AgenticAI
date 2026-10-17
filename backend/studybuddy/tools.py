"""Small deterministic tools: source retrieval, evidence checks, and scoring."""

import re
from difflib import SequenceMatcher


def normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def is_repeat(question: str, previous_questions: list[str]) -> bool:
    canonical = " ".join(re.findall(r"\w+", question.casefold()))
    return any(SequenceMatcher(None, canonical, " ".join(re.findall(r"\w+", previous.casefold()))).ratio() >= 0.85 for previous in previous_questions)


def prepare_notes(notes: str) -> list[dict]:
    notes = notes.strip()
    if len(notes) < 100 or len(notes.split()) < 20:
        raise ValueError("Add at least 100 characters and 20 words of study notes.")
    if len(notes) > 10000:
        raise ValueError("Keep notes within 10,000 characters for this small local-model project.")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", notes) if part.strip()]
    chunks = []
    for paragraph in paragraphs:
        # Preserve exact source text; split long paragraphs at whitespace boundaries.
        parts = re.findall(r"[\s\S]{1,1100}(?:\s+|$)|\S{1100}", paragraph)
        for part in parts:
            chunks.append({"id": f"S{len(chunks) + 1:02d}", "text": part.strip()})
    return chunks


def retrieve_notes(chunks: list[dict], topics: list[str]) -> list[dict]:
    """Lexical retrieval for revision; no embeddings or vector database needed."""
    if not topics:
        return chunks
    terms = set(re.findall(r"[a-zA-Z]{3,}", " ".join(topics).lower()))
    ranked = sorted(chunks, key=lambda c: -len(terms & set(re.findall(r"[a-zA-Z]{3,}", c["text"].lower()))))
    relevant = [c for c in ranked if terms & set(re.findall(r"[a-zA-Z]{3,}", c["text"].lower()))]
    return relevant or chunks


def validate_evidence(lesson: dict, chunks: list[dict], count: int) -> list[str]:
    errors = []
    sources = {c["id"]: normalize(c["text"]) for c in chunks}
    if len(lesson["questions"]) != count:
        errors.append(f"Return exactly {count} questions.")
    seen = set()
    for i, question in enumerate(lesson["questions"], 1):
        if question["source_id"] not in sources:
            errors.append(f"Question {i}: use a source ID from the supplied notes.")
        elif normalize(question["evidence"]) not in sources[question["source_id"]]:
            errors.append(f"Question {i}: evidence must be an exact quote from its source.")
        key = normalize(question["question"])
        if key in seen:
            errors.append(f"Question {i}: avoid duplicate questions.")
        seen.add(key)
    return errors


def score_answers(questions: list[dict], answers: list[int]) -> dict:
    if len(answers) != len(questions):
        raise ValueError("Answer every question before submitting.")
    if any(type(a) is not int or a not in range(4) for a in answers):
        raise ValueError("Choose one valid option for every question.")
    items = []
    weak_topics = []
    for question, answer in zip(questions, answers):
        correct = answer == question["correct_index"]
        items.append({**question, "selected_index": answer, "is_correct": correct})
        if not correct and question["topic"] not in weak_topics:
            weak_topics.append(question["topic"])
    correct_count = sum(item["is_correct"] for item in items)
    return {
        "correct": correct_count,
        "total": len(questions),
        "score": round(100 * correct_count / len(questions), 1),
        "weak_topics": weak_topics,
        "items": items,
    }
