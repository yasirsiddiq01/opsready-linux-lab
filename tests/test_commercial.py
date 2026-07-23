from opsready_lab.services.commercial import is_email, is_https_url, load_commercial_settings


def test_commercial_checkout_is_disabled_by_default() -> None:
    settings = load_commercial_settings({}, {})
    assert not settings.ready_for_live_checkout
    assert "Live sales are disabled." in settings.readiness_issues()


def test_live_checkout_requires_all_safety_gates_and_policies() -> None:
    settings = load_commercial_settings(
        {
            "sales_enabled": True,
            "fulfilment_ready": True,
            "checkout_url": "https://example.lemonsqueezy.com/checkout/buy/test",
            "support_email": "support@example.com",
            "terms_url": "https://example.com/terms",
            "privacy_url": "https://example.com/privacy",
            "refund_url": "https://example.com/refunds",
        },
        {},
    )
    assert settings.ready_for_live_checkout
    assert settings.readiness_issues() == ()


def test_http_and_malformed_contacts_are_rejected() -> None:
    assert not is_https_url("http://example.com")
    assert not is_https_url("javascript:alert(1)")
    assert is_https_url("https://example.com/path")
    assert is_email("support@example.com")
    assert not is_email("support-at-example.com")


def test_waitlist_can_be_enabled_without_live_checkout() -> None:
    settings = load_commercial_settings({"waitlist_url": "https://example.com/waitlist"}, {})
    assert settings.waitlist_available
    assert not settings.ready_for_live_checkout
