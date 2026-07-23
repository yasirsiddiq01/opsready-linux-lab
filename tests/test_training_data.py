from opsready_lab.catalog.commands import COMMAND_LEARNING_GUIDES, COMMANDS, LEVELS
from opsready_lab.catalog.exercises import EXERCISES, exercises_for_level
from opsready_lab.catalog.incidents import INCIDENTS


def test_minimum_content_targets() -> None:
    assert len(COMMANDS) == 150
    assert len(INCIDENTS) == 50
    assert len(EXERCISES) == 45


def test_command_records_are_complete() -> None:
    required = {"level", "category", "area", "summary", "example", "output", "safe", "risk", "flags"}
    for name, item in COMMANDS.items():
        assert required.issubset(item), name
        assert item["level"] in LEVELS
        assert item["example"]
        assert item["flags"]


def test_incident_ids_and_answers() -> None:
    ids = [item["id"] for item in INCIDENTS]
    assert len(ids) == len(set(ids))
    for item in INCIDENTS:
        assert item["level"] in LEVELS
        assert item["answer"] in item["options"]
        assert item["points"] > 0
        assert item["remediation"]


def test_exercise_ids_and_answers() -> None:
    ids = [item["id"] for item in EXERCISES]
    assert len(ids) == len(set(ids))
    for item in EXERCISES:
        assert item["level"] in LEVELS
        assert item["answer"] in item["options"]
        assert item["points"] > 0


def test_every_command_has_complete_learning_guidance() -> None:
    assert set(COMMANDS) == set(COMMAND_LEARNING_GUIDES)
    for guide in COMMAND_LEARNING_GUIDES.values():
        assert set(guide) == {"when", "read", "next"}
        assert all(str(value).strip() for value in guide.values())


def test_each_assessment_level_has_fifteen_questions() -> None:
    for level in LEVELS:
        assert len(exercises_for_level(level)) == 15


def test_command_levels_are_balanced() -> None:
    for level in LEVELS:
        assert sum(1 for item in COMMANDS.values() if item["level"] == level) == 50


def test_incident_catalogue_has_substantial_level_coverage() -> None:
    for level in LEVELS:
        assert sum(1 for item in INCIDENTS if item["level"] == level) >= 16


def test_path_string_command_descriptions_do_not_imply_deletion() -> None:
    from opsready_lab.catalog.commands import COMMANDS, learning_guide

    basename = COMMANDS["basename"]
    dirname = COMMANDS["dirname"]
    assert "does not delete" in str(basename["summary"])
    assert "does not remove" in str(dirname["summary"])
    assert "does not open" in learning_guide("basename")["read"]
    assert "No directory is removed" in learning_guide("dirname")["read"]
