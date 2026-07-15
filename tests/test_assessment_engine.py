from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from opsready_lab.catalog.commands import LEVELS
from opsready_lab.catalog.exercises import exercises_for_level
from opsready_lab.services.assessment_engine import (
    BACKUP_QUESTION_COUNT,
    AssessmentGenerationError,
    AssessmentTest,
    build_backup_test,
    build_curated_test,
    load_test,
    rebuild_curated_test,
    save_test,
    validate_question_bank,
)


def test_curated_test_is_stable_for_saved_seed() -> None:
    first = build_curated_test("Beginner", question_count=10, seed="stable-seed")
    restored = rebuild_curated_test("Beginner", 10, "stable-seed", first.test_id)
    assert [q["question"] for q in first.questions] == [q["question"] for q in restored.questions]
    assert [q["options"] for q in first.questions] == [q["options"] for q in restored.questions]
    assert first.test_id == restored.test_id


def test_new_seed_changes_random_test() -> None:
    first = build_curated_test("Intermediate", question_count=10, seed="seed-one")
    second = build_curated_test("Intermediate", question_count=10, seed="seed-two")
    assert [q["question"] for q in first.questions] != [q["question"] for q in second.questions]


def test_generated_test_contains_no_duplicate_questions() -> None:
    test = build_curated_test("Advanced", question_count=15, seed="no-duplicates")
    texts = [str(question["question"]).strip().lower() for question in test.questions]
    assert len(texts) == len(set(texts))
    assert test.source == "curated-random"


@pytest.mark.parametrize("level", LEVELS)
def test_each_level_keeps_three_reviewed_emergency_questions(level: str) -> None:
    test = build_backup_test(level)
    assert test.source == "reviewed-emergency-backup"
    assert len(test.questions) == BACKUP_QUESTION_COUNT
    assert all(question["answer"] in question["options"] for question in test.questions)


def test_question_bank_validation_rejects_duplicate_id() -> None:
    questions = deepcopy(exercises_for_level("Beginner")[:2])
    questions[1]["id"] = questions[0]["id"]
    with pytest.raises(AssessmentGenerationError, match="Duplicate assessment question ID"):
        validate_question_bank(questions)


def test_question_bank_validation_rejects_duplicate_text() -> None:
    questions = deepcopy(exercises_for_level("Beginner")[:2])
    questions[1]["question"] = questions[0]["question"]
    with pytest.raises(AssessmentGenerationError, match="Duplicate assessment question text"):
        validate_question_bank(questions)


def test_test_cache_round_trip(tmp_path: Path) -> None:
    test = build_curated_test("Advanced", question_count=5, seed="cache-seed")
    save_test(test, cache_dir=tmp_path)
    loaded = load_test(test.test_id, cache_dir=tmp_path)
    assert isinstance(loaded, AssessmentTest)
    assert loaded.test_id == test.test_id
    assert loaded.questions == test.questions
