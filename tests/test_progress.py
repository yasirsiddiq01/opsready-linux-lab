from opsready_lab.services.progress import initialise_progress, record_exercise, record_incident, score_percent


def test_progress_scores_only_once() -> None:
    state = {}
    initialise_progress(state)
    assert record_exercise(state, "Q001", True, 5)
    assert not record_exercise(state, "Q001", True, 5)
    assert state["score"] == 5
    assert state["possible_score"] == 5


def test_incident_scores_only_once() -> None:
    state = {}
    initialise_progress(state)
    assert record_incident(state, "INC-001", 10, 10)
    assert not record_incident(state, "INC-001", 10, 10)
    assert score_percent(int(state["score"]), int(state["possible_score"])) == 100


def test_zero_possible_score() -> None:
    assert score_percent(0, 0) == 0
