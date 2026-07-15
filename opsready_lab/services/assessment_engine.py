from __future__ import annotations

import hashlib
import json
import os
import random
import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from opsready_lab.catalog.exercises import EXERCISES, Exercise, exercises_for_level

DEFAULT_QUESTION_COUNT = 10
BACKUP_QUESTION_COUNT = 3


class AssessmentGenerationError(RuntimeError):
    """Raised when a reviewed assessment cannot be built or restored safely."""


@dataclass
class AssessmentTest:
    test_id: str
    level: str
    source: str
    questions: list[Exercise]
    created_at_utc: str
    seed: str
    notice: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> AssessmentTest:
        level = str(value.get("level", "Beginner"))
        questions = [normalise_stored_question(item, fallback_level=level) for item in value["questions"]]
        return cls(
            test_id=str(value["test_id"]),
            level=level,
            source=str(value["source"]),
            questions=questions,
            created_at_utc=str(value["created_at_utc"]),
            seed=str(value.get("seed", "")),
            notice=str(value.get("notice", "")),
        )


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def stable_rng(seed: str) -> random.Random:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def new_test_id() -> str:
    return f"TST-{uuid4().hex[:12].upper()}"


def question_fingerprint(text: str) -> str:
    normalised = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def validate_question_bank(questions: list[Exercise]) -> None:
    """Reject duplicate IDs, duplicate question text, or malformed reviewed records."""

    ids: set[str] = set()
    fingerprints: set[str] = set()
    for item in questions:
        normalised = normalise_stored_question(item, fallback_level=str(item.get("level", "Beginner")))
        question_id = str(normalised["id"])
        fingerprint = question_fingerprint(str(normalised["question"]))
        if question_id in ids:
            raise AssessmentGenerationError(f"Duplicate assessment question ID: {question_id}")
        if fingerprint in fingerprints:
            raise AssessmentGenerationError("Duplicate assessment question text was detected in the reviewed bank.")
        ids.add(question_id)
        fingerprints.add(fingerprint)


def copy_and_shuffle_question(question: Exercise, rng: random.Random, prefix: str = "") -> Exercise:
    copied = deepcopy(question)
    options = [str(item) for item in copied["options"]]
    rng.shuffle(options)
    copied["options"] = options
    if prefix:
        copied["id"] = f"{prefix}-{copied['id']}"
    return copied


def build_curated_test(
    level: str,
    question_count: int = DEFAULT_QUESTION_COUNT,
    seed: str | None = None,
) -> AssessmentTest:
    available = exercises_for_level(level)
    if not available:
        raise AssessmentGenerationError(f"No reviewed questions are available for level: {level}")
    validate_question_bank(available)

    actual_seed = seed or uuid4().hex
    rng = stable_rng(actual_seed)
    count = max(1, min(int(question_count), len(available)))
    selected = rng.sample(available, count)
    test_id = new_test_id()
    questions = [copy_and_shuffle_question(item, rng, prefix=test_id) for item in selected]
    return AssessmentTest(
        test_id=test_id,
        level=level,
        source="curated-random",
        questions=questions,
        created_at_utc=utc_now_iso(),
        seed=actual_seed,
        notice=f"Generated without duplicates from the reviewed {len(EXERCISES)}-question bank.",
    )


def rebuild_curated_test(level: str, question_count: int, seed: str, test_id: str) -> AssessmentTest:
    available = exercises_for_level(level)
    if not available:
        raise AssessmentGenerationError(f"No reviewed questions are available for level: {level}")
    validate_question_bank(available)

    rng = stable_rng(seed)
    count = max(1, min(int(question_count), len(available)))
    selected = rng.sample(available, count)
    questions = [copy_and_shuffle_question(item, rng, prefix=test_id) for item in selected]
    return AssessmentTest(
        test_id=test_id,
        level=level,
        source="curated-random",
        questions=questions,
        created_at_utc=utc_now_iso(),
        seed=seed,
        notice="Restored from the reviewed question bank using the saved test seed.",
    )


def backup_questions_for_level(level: str) -> list[Exercise]:
    """Return a small reviewed emergency set; it is not exposed as a learner option."""

    reviewed = exercises_for_level(level)
    if len(reviewed) < BACKUP_QUESTION_COUNT:
        raise AssessmentGenerationError(f"The {level} emergency backup bank is incomplete.")
    validate_question_bank(reviewed)
    rng = stable_rng(f"opsready-backup-{level}")
    return [
        copy_and_shuffle_question(item, rng, prefix=f"BACKUP-{level[:1].upper()}")
        for item in reviewed[:BACKUP_QUESTION_COUNT]
    ]


def build_backup_test(level: str, reason: str = "") -> AssessmentTest:
    return AssessmentTest(
        test_id=new_test_id(),
        level=level,
        source="reviewed-emergency-backup",
        questions=backup_questions_for_level(level),
        created_at_utc=utc_now_iso(),
        seed=f"backup-{level.lower()}",
        notice=(
            "The main reviewed bank could not be loaded, so a reviewed three-question emergency test was used."
            + (f" Details: {reason}" if reason else "")
        ),
    )


def normalise_stored_question(value: dict[str, Any], fallback_level: str) -> Exercise:
    if not isinstance(value, dict):
        raise AssessmentGenerationError("Assessment question must be an object.")

    question_id = str(value.get("id", "")).strip()
    question = str(value.get("question", "")).strip()
    topic = str(value.get("topic", "Linux operations")).strip() or "Linux operations"
    explanation = str(value.get("explanation", "")).strip()
    answer = str(value.get("answer", "")).strip()
    level = str(value.get("level", fallback_level)).strip() or fallback_level
    raw_options = value.get("options", [])

    if not question_id:
        raise AssessmentGenerationError("Assessment question ID is missing.")
    if not question or len(question) < 8:
        raise AssessmentGenerationError("Assessment question text is missing or too short.")
    if not isinstance(raw_options, list) or len(raw_options) < 2:
        raise AssessmentGenerationError("Assessment question must contain at least two options.")
    options = [str(item).strip() for item in raw_options]
    if any(not option for option in options) or len(set(options)) != len(options):
        raise AssessmentGenerationError("Assessment options must be unique non-empty strings.")
    if answer not in options:
        raise AssessmentGenerationError("Assessment answer must exactly match one option.")
    if not explanation:
        raise AssessmentGenerationError("Assessment explanation is missing.")

    points_by_level = {"Beginner": 5, "Intermediate": 10, "Advanced": 15}
    return {
        "id": question_id,
        "level": level,
        "topic": topic,
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "points": int(value.get("points", points_by_level.get(level, 10))),
    }


def configured_cache_dir() -> Path:
    configured = os.getenv("OPSREADY_ASSESSMENT_CACHE_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(".runtime") / "assessment_tests"


def safe_test_id(test_id: str) -> str:
    if not re.fullmatch(r"TST-[A-Z0-9]{12}", test_id):
        raise AssessmentGenerationError("Invalid assessment test identifier.")
    return test_id


def save_test(test: AssessmentTest, cache_dir: Path | None = None) -> Path:
    destination_dir = cache_dir or configured_cache_dir()
    destination_dir.mkdir(parents=True, exist_ok=True)
    path = destination_dir / f"{safe_test_id(test.test_id)}.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(test.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return path


def load_test(test_id: str, cache_dir: Path | None = None) -> AssessmentTest | None:
    try:
        identifier = safe_test_id(test_id)
    except AssessmentGenerationError:
        return None
    path = (cache_dir or configured_cache_dir()) / f"{identifier}.json"
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        test = AssessmentTest.from_dict(raw)
        if test.source not in {"curated-random", "reviewed-emergency-backup"}:
            return None
        return test
    except (OSError, KeyError, TypeError, json.JSONDecodeError, AssessmentGenerationError):
        return None


def curated_bank_size() -> int:
    return len(EXERCISES)
