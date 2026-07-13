from __future__ import annotations

import argparse
import curses
import os
import sys

from blinkbox.config import UserConfig
from blinkbox.tools.device import scan_devices
from blinkbox.ui.tui import BlinkBoxTUI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blinkbox")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("tui", help="Launch the interactive terminal interface")
    subparsers.add_parser("devices", help="List connected ADB and fastboot devices")
    return parser


def run_devices() -> int:
    devices = scan_devices()
    if not devices:
        print("No ADB or fastboot devices detected.")
        return 1
    for device in devices:
        print(f"{device.transport}\t{device.serial}\t{device.state}")
    return 0


def run_tui(config: UserConfig) -> int:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("The TUI requires an interactive terminal. Try: ssh -t host blinkbox", file=sys.stderr)
        return 2
    os.environ.setdefault("ESCDELAY", "25")
    curses.wrapper(lambda screen: BlinkBoxTUI(screen, config).run())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = UserConfig.from_environment()

    if args.command == "devices":
        return run_devices()
    return run_tui(config)
