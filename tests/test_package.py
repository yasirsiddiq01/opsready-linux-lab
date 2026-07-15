from pathlib import Path

from opsready_lab import __version__
from opsready_lab.config import APP_NAME, APP_SLUG


def test_package_metadata() -> None:
    assert __version__ == "1.5.2"
    assert APP_NAME == "OpsReady Linux Lab"
    assert APP_SLUG == "opsready-linux-lab"


def test_dropdown_contrast_css_targets_widget_and_portal_layers() -> None:
    theme = (Path(__file__).resolve().parents[1] / "opsready_lab" / "ui" / "theme.py").read_text()
    assert '[data-testid="stSelectbox"] [role="combobox"]' in theme
    assert 'body > div[data-baseweb="popover"]' in theme
    assert '[data-baseweb="popover"] [role="option"]' in theme
