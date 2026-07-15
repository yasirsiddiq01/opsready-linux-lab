from __future__ import annotations

from collections.abc import MutableMapping

STATE_DEFAULTS = {
    "completed_commands": set(),
    "completed_incidents": set(),
    "answered_exercises": {},
    "score": 0,
    "possible_score": 0,
    "assessment_index": 0,
    "assessment_finished": False,
}


def initialise_progress(state: MutableMapping[str, object]) -> None:
    for key, value in STATE_DEFAULTS.items():
        if key not in state:
            state[key] = value.copy() if hasattr(value, "copy") else value


def record_command(state: MutableMapping[str, object], command: str) -> None:
    commands = state["completed_commands"]
    assert isinstance(commands, set)
    commands.add(command)


def record_incident(state: MutableMapping[str, object], incident_id: str, awarded: int, possible: int) -> bool:
    incidents = state["completed_incidents"]
    assert isinstance(incidents, set)
    if incident_id in incidents:
        return False
    incidents.add(incident_id)
    state["score"] = int(state["score"]) + awarded
    state["possible_score"] = int(state["possible_score"]) + possible
    return True


def record_exercise(state: MutableMapping[str, object], exercise_id: str, correct: bool, points: int) -> bool:
    answers = state["answered_exercises"]
    assert isinstance(answers, dict)
    if exercise_id in answers:
        return False
    answers[exercise_id] = correct
    state["score"] = int(state["score"]) + (points if correct else 0)
    state["possible_score"] = int(state["possible_score"]) + points
    return True


def score_percent(score: int, possible: int) -> int:
    if possible <= 0:
        return 0
    return round((score / possible) * 100)


def reset_progress(state: MutableMapping[str, object]) -> None:
    for key in list(STATE_DEFAULTS):
        state.pop(key, None)
    initialise_progress(state)
