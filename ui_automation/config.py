"""Environment-based configuration for UI automation."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class UISettings:
    base_url: str
    username: str = ""
    password: str = ""
    browser: str = "chromium"
    headless: bool = True
    timeout: float = 10.0
    slow_mo: float = 0.0
    artifacts_dir: Path = Path("test-results/ui")
    trace: bool = False

    @classmethod
    def from_env(cls) -> "UISettings":
        base_url = os.getenv("UI_BASE_URL", "").strip()
        if not base_url:
            raise ValueError("UI_BASE_URL is required")
        return cls(
            base_url=base_url.rstrip("/"),
            username=os.getenv("UI_USERNAME", ""),
            password=os.getenv("UI_PASSWORD", ""),
            browser=os.getenv("UI_BROWSER", "chromium").lower(),
            headless=_as_bool(os.getenv("UI_HEADLESS", "true")),
            timeout=float(os.getenv("UI_TIMEOUT", "10")),
            slow_mo=float(os.getenv("UI_SLOW_MO", "0")),
            artifacts_dir=Path(os.getenv("UI_ARTIFACTS_DIR", "test-results/ui")),
            trace=_as_bool(os.getenv("UI_TRACE", "false")),
        )


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}