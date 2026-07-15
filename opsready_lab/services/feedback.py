"""Feedback validation and delivery for the free public preview.

The public app can send JSON feedback to a configured webhook. A local JSONL
file is also used as a fallback for development and single-instance testing.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

DEFAULT_FEEDBACK_FILE = Path("runtime/feedback.jsonl")
MAX_TEXT_LENGTH = 4_000


@dataclass(frozen=True)
class FeedbackRecord:
    """A single structured feedback submission."""

    submission_id: str
    submitted_at_utc: str
    app_version: str
    session_id: str
    role: str
    linux_experience: str
    feedback_types: list[str]
    sections_used: list[str]
    usefulness_rating: int
    ease_rating: int
    confidence_rating: int
    recommendation_score: int
    most_useful: str
    improvement_needed: str
    missing_content: str
    issue_found: bool
    issue_details: str
    email: str
    consent_to_feedback_use: bool
    consent_to_contact: bool
    source: str = "in_app_form"

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-serialisable dictionary."""

        return asdict(self)


def clean_text(value: str, limit: int = MAX_TEXT_LENGTH) -> str:
    """Normalise whitespace and enforce a predictable storage limit."""

    return " ".join(str(value).strip().split())[:limit]


def create_feedback_record(
    *,
    app_version: str,
    session_id: str,
    role: str,
    linux_experience: str,
    feedback_types: list[str],
    sections_used: list[str],
    usefulness_rating: int,
    ease_rating: int,
    confidence_rating: int,
    recommendation_score: int,
    most_useful: str,
    improvement_needed: str,
    missing_content: str,
    issue_found: bool,
    issue_details: str,
    email: str,
    consent_to_feedback_use: bool,
    consent_to_contact: bool,
) -> FeedbackRecord:
    """Build a normalised feedback record with server-side metadata."""

    return FeedbackRecord(
        submission_id=str(uuid4()),
        submitted_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        app_version=clean_text(app_version, 40),
        session_id=clean_text(session_id, 100),
        role=clean_text(role, 100),
        linux_experience=clean_text(linux_experience, 100),
        feedback_types=[clean_text(item, 100) for item in feedback_types],
        sections_used=[clean_text(item, 100) for item in sections_used],
        usefulness_rating=int(usefulness_rating),
        ease_rating=int(ease_rating),
        confidence_rating=int(confidence_rating),
        recommendation_score=int(recommendation_score),
        most_useful=clean_text(most_useful),
        improvement_needed=clean_text(improvement_needed),
        missing_content=clean_text(missing_content),
        issue_found=bool(issue_found),
        issue_details=clean_text(issue_details),
        email=clean_text(email, 254),
        consent_to_feedback_use=bool(consent_to_feedback_use),
        consent_to_contact=bool(consent_to_contact),
    )


def validate_feedback(record: FeedbackRecord) -> list[str]:
    """Return user-correctable validation errors."""

    errors: list[str] = []
    if not record.role:
        errors.append("Select the option that best describes you.")
    if not record.linux_experience:
        errors.append("Select your Linux experience level.")
    if not record.feedback_types:
        errors.append("Select at least one feedback category.")
    if not record.sections_used:
        errors.append("Select at least one section you used.")
    for label, value in (
        ("usefulness", record.usefulness_rating),
        ("ease of use", record.ease_rating),
        ("confidence improvement", record.confidence_rating),
    ):
        if value not in range(1, 6):
            errors.append(f"The {label} rating must be between 1 and 5.")
    if record.recommendation_score not in range(0, 11):
        errors.append("The recommendation score must be between 0 and 10.")
    if not record.improvement_needed:
        errors.append("Describe at least one improvement or say that no change is needed.")
    if record.issue_found and not record.issue_details:
        errors.append("Describe the problem you encountered.")
    if record.email and ("@" not in record.email or record.email.startswith("@") or record.email.endswith("@")):
        errors.append("Enter a valid email address or leave the email field blank.")
    if record.consent_to_contact and not record.email:
        errors.append("Provide an email address if you want to be contacted.")
    if not record.consent_to_feedback_use:
        errors.append("Consent is required to store and use this feedback for product improvement.")
    return errors


def feedback_file_from_environment() -> Path:
    """Resolve the local fallback path without requiring configuration."""

    configured = os.getenv("OPSREADY_FEEDBACK_FILE", "").strip()
    return Path(configured) if configured else DEFAULT_FEEDBACK_FILE


def save_feedback_locally(record: FeedbackRecord, file_path: Path | None = None) -> Path:
    """Append one record to a UTF-8 JSONL file."""

    destination = file_path or feedback_file_from_environment()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_payload(), ensure_ascii=False) + "\n")
    return destination


def valid_webhook_url(url: str) -> bool:
    """Allow only explicit HTTP(S) webhook endpoints."""

    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def post_feedback_webhook(record: FeedbackRecord, webhook_url: str, timeout_seconds: int = 8) -> None:
    """POST a feedback record as JSON and raise on delivery failure."""

    if not valid_webhook_url(webhook_url):
        raise ValueError("Feedback webhook must be a valid HTTP or HTTPS URL.")

    body = json.dumps(record.to_payload(), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "OpsReady-Linux-Lab-Feedback/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError(f"Feedback endpoint returned HTTP {response.status}.")
            response_body = response.read().decode("utf-8", errors="replace").strip()
            if response_body:
                try:
                    response_data = json.loads(response_body)
                except json.JSONDecodeError:
                    response_data = None
                if isinstance(response_data, dict) and response_data.get("ok") is False:
                    raise RuntimeError("Feedback endpoint reported that the submission was not stored.")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Feedback endpoint returned HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("Feedback endpoint could not be reached.") from exc


@dataclass(frozen=True)
class FeedbackDeliveryResult:
    """Outcome used by the user interface without exposing sensitive details."""

    accepted: bool
    delivered_to_webhook: bool
    saved_locally: bool
    submission_id: str
    message: str


def submit_feedback(
    record: FeedbackRecord,
    *,
    webhook_url: str = "",
    local_file: Path | None = None,
) -> FeedbackDeliveryResult:
    """Validate, save a fallback copy, and deliver to a configured webhook."""

    errors = validate_feedback(record)
    if errors:
        return FeedbackDeliveryResult(False, False, False, record.submission_id, " ".join(errors))

    local_saved = False
    local_error: Exception | None = None
    try:
        save_feedback_locally(record, local_file)
        local_saved = True
    except OSError as exc:
        local_error = exc

    webhook = webhook_url.strip()
    if webhook:
        try:
            post_feedback_webhook(record, webhook)
            return FeedbackDeliveryResult(
                True,
                True,
                local_saved,
                record.submission_id,
                "Feedback submitted successfully.",
            )
        except (RuntimeError, ValueError) as exc:
            if local_saved:
                return FeedbackDeliveryResult(
                    True,
                    False,
                    True,
                    record.submission_id,
                    "Feedback was saved as a local fallback because the configured endpoint was unavailable.",
                )
            return FeedbackDeliveryResult(False, False, False, record.submission_id, str(exc))

    if local_saved:
        return FeedbackDeliveryResult(
            True,
            False,
            True,
            record.submission_id,
            "Feedback was saved in local preview storage.",
        )

    detail = f" Local storage error: {local_error}" if local_error else ""
    return FeedbackDeliveryResult(
        False,
        False,
        False,
        record.submission_id,
        f"Feedback could not be stored.{detail}",
    )
