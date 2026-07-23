from pathlib import Path

from opsready_lab import __version__
from opsready_lab.config import APP_NAME, APP_SLUG


def test_package_metadata() -> None:
    assert __version__ == "1.7.1"
    assert APP_NAME == "OpsReady Linux Lab"
    assert APP_SLUG == "opsready-linux-lab"


def test_dropdown_contrast_css_targets_widget_and_portal_layers() -> None:
    theme = (Path(__file__).resolve().parents[1] / "opsready_lab" / "ui" / "theme.py").read_text()
    assert '[data-testid="stSelectbox"] [role="combobox"]' in theme
    assert 'body > div[data-baseweb="popover"]' in theme
    assert '[data-baseweb="popover"] [role="option"]' in theme


def test_sidebar_reset_button_contrast_and_pro_roadmap_are_present() -> None:
    project = Path(__file__).resolve().parents[1]
    app = (project / "app.py").read_text(encoding="utf-8")
    theme = (project / "opsready_lab" / "ui" / "theme.py").read_text(encoding="utf-8")

    assert 'key="reset_session_progress"' in app
    assert ".st-key-reset_session_progress button" in theme
    assert "background:#334155 !important" in theme
    assert "Pro delivery roadmap" in app
    assert "1. Foundation" in app
    assert "2. Founding beta" in app
    assert "3. Instructor and cohort tools" in app
