from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    maintainer_name: str
    git_username: str
    git_email: str
    android_root: Path
    roms_root: Path
    recoveries_root: Path
    tools_root: Path
    releases_root: Path
    default_editor: str
    remote_host: str
    is_termux: bool


def _path(name: str, fallback: Path) -> Path:
    return Path(os.environ.get(name, str(fallback))).expanduser()


def load_settings() -> Settings:
    home = Path.home()
    android_root = _path("BLINKBOX_ANDROID_ROOT", home / "Android")
    return Settings(
        maintainer_name=os.environ.get("BLINKBOX_MAINTAINER_NAME", "Unknown maintainer"),
        git_username=os.environ.get("BLINKBOX_GIT_USERNAME", ""),
        git_email=os.environ.get("BLINKBOX_GIT_EMAIL", ""),
        android_root=android_root,
        roms_root=_path("BLINKBOX_ROMS_ROOT", android_root / "ROMs"),
        recoveries_root=_path("BLINKBOX_RECOVERIES_ROOT", android_root / "Recoveries"),
        tools_root=_path("BLINKBOX_TOOLS_ROOT", android_root / "Tools"),
        releases_root=_path("BLINKBOX_RELEASES_ROOT", android_root / "Releases"),
        default_editor=os.environ.get("BLINKBOX_DEFAULT_EDITOR", "nano"),
        remote_host=os.environ.get("BLINKBOX_REMOTE_HOST", ""),
        is_termux=bool(os.environ.get("TERMUX_VERSION"))
        or Path("/data/data/com.termux/files/usr").is_dir(),
    )
