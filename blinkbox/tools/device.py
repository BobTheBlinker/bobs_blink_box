from __future__ import annotations

from dataclasses import dataclass
import shutil
import subprocess
from typing import Sequence


@dataclass(frozen=True)
class Device:
    transport: str
    serial: str
    state: str


def _run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def scan_devices() -> list[Device]:
    devices: list[Device] = []

    if shutil.which("adb"):
        result = _run(["adb", "devices"])
        for line in result.stdout.splitlines()[1:]:
            fields = line.split()
            if len(fields) >= 2:
                devices.append(Device("adb", fields[0], fields[1]))

    if shutil.which("fastboot"):
        result = _run(["fastboot", "devices"])
        for line in result.stdout.splitlines():
            fields = line.split()
            if fields:
                state = fields[1] if len(fields) > 1 else "fastboot"
                devices.append(Device("fastboot", fields[0], state))

    return devices


def format_devices() -> str:
    devices = scan_devices()
    if not devices:
        return "No ADB or fastboot devices detected."

    width = max(len(item.transport) for item in devices)
    return "\n".join(
        f"{item.transport:<{width}}  {item.serial}  {item.state}" for item in devices
    )
