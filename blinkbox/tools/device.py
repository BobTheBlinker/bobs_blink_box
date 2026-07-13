from __future__ import annotations

from dataclasses import dataclass
import shutil
import subprocess
from typing import Iterable


@dataclass(frozen=True)
class DeviceLine:
    transport: str
    serial: str
    state: str


def _run(command: Iterable[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        timeout=8,
    )


def scan_devices() -> list[DeviceLine]:
    found: list[DeviceLine] = []

    if shutil.which("adb"):
        result = _run(["adb", "devices"])
        for line in result.stdout.splitlines()[1:]:
            fields = line.strip().split()
            if len(fields) >= 2:
                found.append(DeviceLine("adb", fields[0], fields[1]))

    if shutil.which("fastboot"):
        result = _run(["fastboot", "devices"])
        for line in result.stdout.splitlines():
            fields = line.strip().split()
            if fields:
                state = fields[1] if len(fields) > 1 else "fastboot"
                found.append(DeviceLine("fastboot", fields[0], state))

    return found


def tool_status() -> list[str]:
    lines = []
    for tool in ("adb", "fastboot", "git", "ssh"):
        path = shutil.which(tool)
        lines.append(f"{tool:<10} {'available' if path else 'missing'}{f'  {path}' if path else ''}")
    return lines
