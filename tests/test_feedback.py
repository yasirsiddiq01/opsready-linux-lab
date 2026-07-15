from dataclasses import replace
from pathlib import Path

from opsready_lab.services.feedback import (
    create_feedback_record,
    submit_feedback,
    valid_webhook_url,
    validate_feedback,
)


def valid_record():
    return create_feedback_record(
        app_version="1.5.2",
        session_id="test-session",
        role="Learner",
        linux_experience="Beginner",
        feedback_types=["Usability"],
        sections_used=["Command Lab"],
        usefulness_rating=5,
        ease_rating=4,
        confidence_rating=4,
        recommendation_score=9,
        most_useful="Command explanations",
        improvement_needed="Add more incidents",
        missing_content="Networking practice",
        issue_found=False,
        issue_details="",
        email="",
        consent_to_feedback_use=True,
        consent_to_contact=False,
    )


def test_valid_feedback_has_no_errors() -> None:
    assert validate_feedback(valid_record()) == []


def test_issue_description_is_required_when_issue_is_reported() -> None:
    record = replace(valid_record(), issue_found=True, issue_details="")
    assert "Describe the problem you encountered." in validate_feedback(record)


def test_feedback_is_saved_as_jsonl(tmp_path: Path) -> None:
    target = tmp_path / "feedback.jsonl"
    result = submit_feedback(valid_record(), local_file=target)
    assert result.accepted
    assert result.saved_locally
    assert not result.delivered_to_webhook
    assert target.read_text(encoding="utf-8").count("\n") == 1
    assert "Add more incidents" in target.read_text(encoding="utf-8")


def test_webhook_validation() -> None:
    assert valid_webhook_url("https://example.com/webhook")
    assert not valid_webhook_url("file:///tmp/feedback")
    assert not valid_webhook_url("javascript:alert(1)")
