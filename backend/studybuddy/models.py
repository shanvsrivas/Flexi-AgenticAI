"""Validate model output before showing it to a student."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DraftQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    topic: str = Field(min_length=2, max_length=90)
    question: str = Field(min_length=10, max_length=450)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3, strict=True)
    explanation: str = Field(min_length=15, max_length=650)
    source_id: str

    @model_validator(mode="after")
    def distinct_options(self):
        clean = [option.strip().casefold() for option in self.options]
        if any(not option for option in clean) or len(set(clean)) != 4:
            raise ValueError("Each question needs four nonempty, distinct options.")
        referential = r"\b(?:all|none) of (?:the )?(?:above|these)|\b(?:both|either) (?:options? )?[a-d] (?:and|or|&) (?:options? )?[a-d]\b"
        if any(re.search(referential, option) for option in clean):
            raise ValueError("Use self-contained options; do not use 'both A and B', 'all of the above', or 'none of the above'.")
        return self


class Question(DraftQuestion):
    evidence: str = Field(min_length=15, max_length=1200)


class DraftLesson(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=100)
    overview: str = Field(min_length=20, max_length=700)
    takeaways: list[str] = Field(min_length=2, max_length=5)
    strategy: str = Field(min_length=15, max_length=400)
    questions: list[DraftQuestion] = Field(min_length=3, max_length=5)


class Lesson(DraftLesson):
    questions: list[Question] = Field(min_length=3, max_length=5)


class AgentDecision(BaseModel):
    """A model-selected tool and its bounded arguments, not a hidden reasoning trace."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    tool: Literal["create_quiz", "explain_concept", "worked_example", "simplify_concept", "ask_clarification", "finish"]
    topics: list[str] = Field(max_length=5)
    difficulty: Literal["Foundation", "Standard", "Challenge"]
    question_style: Literal["recall", "application"]
    reason: str = Field(min_length=10, max_length=400)
    question: str = Field(max_length=400)


class DraftTeachingCard(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    topic: str = Field(min_length=2, max_length=90)
    misconception: str = Field(min_length=15, max_length=650)
    explanation: str = Field(min_length=30, max_length=1200)
    example: str = Field(min_length=20, max_length=900)
    extra_info: str = Field(min_length=15, max_length=650)
    check_question: str = Field(min_length=10, max_length=350)
    source_id: str


class TeachingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cards: list[DraftTeachingCard] = Field(min_length=1, max_length=5)
