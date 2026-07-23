#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from opsready_lab.services.commercial import load_commercial_settings  # noqa: E402


def load_secrets() -> dict[str, object]:
    path = ROOT / ".streamlit" / "secrets.toml"
    if not path.exists() or tomllib is None:
        return {}
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("commercial", {})
    return dict(section) if isinstance(section, dict) else {}


def main() -> int:
    settings = load_commercial_settings(load_secrets(), os.environ)
    issues = settings.readiness_issues()
    print("OpsReady commercial readiness")
    print("=" * 31)
    if not issues:
        print("READY: all application-side checkout gates are complete.")
        print("Run a full Lemon Squeezy test purchase before enabling public promotion.")
        return 0
    print("NOT READY")
    for issue in issues:
        print(f"- {issue}")
    print("\nThe Plans page will not show a live checkout button until every issue is resolved.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
