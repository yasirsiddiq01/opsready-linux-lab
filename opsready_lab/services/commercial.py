from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

_TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _as_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _TRUE_VALUES


def _text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def is_https_url(value: str) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def is_email(value: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(value.strip()))


@dataclass(frozen=True)
class CommercialSettings:
    sales_enabled: bool
    fulfilment_ready: bool
    checkout_url: str
    waitlist_url: str
    customer_portal_url: str
    support_email: str
    terms_url: str
    privacy_url: str
    refund_url: str
    monthly_price_label: str
    annual_price_label: str

    def readiness_issues(self) -> tuple[str, ...]:
        issues: list[str] = []
        if not self.sales_enabled:
            issues.append("Live sales are disabled.")
        if not self.fulfilment_ready:
            issues.append("Paid-user fulfilment is not marked ready.")
        if not is_https_url(self.checkout_url):
            issues.append("A valid HTTPS checkout URL is not configured.")
        if not is_email(self.support_email):
            issues.append("A valid support email is not configured.")
        for label, url in (
            ("Terms", self.terms_url),
            ("Privacy", self.privacy_url),
            ("Refund", self.refund_url),
        ):
            if not is_https_url(url):
                issues.append(f"A valid HTTPS {label.lower()} policy URL is not configured.")
        return tuple(issues)

    @property
    def ready_for_live_checkout(self) -> bool:
        return not self.readiness_issues()

    @property
    def waitlist_available(self) -> bool:
        return is_https_url(self.waitlist_url)

    @property
    def portal_available(self) -> bool:
        return is_https_url(self.customer_portal_url)


def load_commercial_settings(
    values: Mapping[str, object] | None = None,
    environ: Mapping[str, str] | None = None,
) -> CommercialSettings:
    values = values or {}
    environ = environ or os.environ

    def get(secret_key: str, env_key: str, default: str = "") -> str:
        secret_value = _text(values.get(secret_key))
        if secret_value:
            return secret_value
        return _text(environ.get(env_key, default))

    def get_bool(secret_key: str, env_key: str, default: bool = False) -> bool:
        if secret_key in values:
            return _as_bool(values.get(secret_key), default)
        return _as_bool(environ.get(env_key), default)

    return CommercialSettings(
        sales_enabled=get_bool("sales_enabled", "OPSREADY_SALES_ENABLED", False),
        fulfilment_ready=get_bool("fulfilment_ready", "OPSREADY_FULFILMENT_READY", False),
        checkout_url=get("checkout_url", "OPSREADY_CHECKOUT_URL"),
        waitlist_url=get("waitlist_url", "OPSREADY_WAITLIST_URL"),
        customer_portal_url=get("customer_portal_url", "OPSREADY_CUSTOMER_PORTAL_URL"),
        support_email=get("support_email", "OPSREADY_SUPPORT_EMAIL"),
        terms_url=get("terms_url", "OPSREADY_TERMS_URL"),
        privacy_url=get("privacy_url", "OPSREADY_PRIVACY_URL"),
        refund_url=get("refund_url", "OPSREADY_REFUND_URL"),
        monthly_price_label=get("monthly_price_label", "OPSREADY_MONTHLY_PRICE_LABEL", "Price to be confirmed"),
        annual_price_label=get("annual_price_label", "OPSREADY_ANNUAL_PRICE_LABEL", "Price to be confirmed"),
    )
