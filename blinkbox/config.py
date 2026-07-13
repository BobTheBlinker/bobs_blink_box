from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class UserConfig:
    maintainer_name: str
    git_username: str
    git_email: str
    android_root: Path
    roms_root: Path
    recoveries_root: Path
    tools_root: Path
    releases_root: Path
    editor: str
    remote_host: str
    config_dir: Path
    state_dir: Path

    @classmethod
    def from_environment(cls) -> "UserConfig":
        home = Path.home()
        android_root = Path(
            os.getenv("BLINKBOX_ANDROID_ROOT", str(home / "Android"))
        ).expanduser()

        return cls(
            maintainer_name=os.getenv("BLINKBOX_MAINTAINER_NAME", "Unknown Maintainer"),
            git_username=os.getenv("BLINKBOX_GIT_USERNAME", ""),
            git_email=os.getenv("BLINKBOX_GIT_EMAIL", ""),
            android_root=android_root,
            roms_root=Path(
                os.getenv("BLINKBOX_ROMS_ROOT", str(android_root / "ROMs"))
            ).expanduser(),
            recoveries_root=Path(
                os.getenv("BLINKBOX_RECOVERIES_ROOT", str(android_root / "Recoveries"))
            ).expanduser(),
            tools_root=Path(
                os.getenv("BLINKBOX_TOOLS_ROOT", str(android_root / "Tools"))
            ).expanduser(),
            releases_root=Path(
                os.getenv(
                    "BLINKBOX_RELEASES_ROOT",
                    os.getenv("BLINKBOX_RELEASE_ROOT", str(android_root / "Releases")),
                )
            ).expanduser(),
            editor=os.getenv("BLINKBOX_EDITOR", "nano"),
            remote_host=os.getenv("BLINKBOX_REMOTE_HOST", ""),
            config_dir=Path(
                os.getenv("BLINKBOX_CONFIG_DIR", str(home / ".config/blinkbox"))
            ).expanduser(),
            state_dir=Path(
                os.getenv("BLINKBOX_STATE_DIR", str(home / ".local/state/blinkbox"))
            ).expanduser(),
        )
