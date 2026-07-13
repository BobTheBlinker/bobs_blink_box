from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class UserConfig:
    maintainer_name: str
    git_username: str
    git_email: str
    build_root: Path
    release_root: Path
    editor: str
    remote_host: str
    config_dir: Path
    state_dir: Path

    @classmethod
    def from_environment(cls) -> "UserConfig":
        home = Path.home()
        return cls(
            maintainer_name=os.getenv("BLINKBOX_MAINTAINER_NAME", "Unknown Maintainer"),
            git_username=os.getenv("BLINKBOX_GIT_USERNAME", ""),
            git_email=os.getenv("BLINKBOX_GIT_EMAIL", ""),
            build_root=Path(os.getenv("BLINKBOX_BUILD_ROOT", str(home / "builds"))).expanduser(),
            release_root=Path(os.getenv("BLINKBOX_RELEASE_ROOT", str(home / "releases"))).expanduser(),
            editor=os.getenv("BLINKBOX_EDITOR", "nano"),
            remote_host=os.getenv("BLINKBOX_REMOTE_HOST", ""),
            config_dir=Path(os.getenv("BLINKBOX_CONFIG_DIR", str(home / ".config/blinkbox"))).expanduser(),
            state_dir=Path(os.getenv("BLINKBOX_STATE_DIR", str(home / ".local/state/blinkbox"))).expanduser(),
        )
