from __future__ import annotations

import argparse
import curses
import sys

from blinkbox import __version__
from blinkbox.config import load_settings
from blinkbox.tools.device import format_devices
from blinkbox.ui.tui import run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blinkbox")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("devices", help="list connected ADB and fastboot devices")
    subparsers.add_parser("config", help="print active workspace settings")
    return parser


def print_config() -> None:
    settings = load_settings()
    print(f"Maintainer: {settings.maintainer_name}")
    print(f"Android root: {settings.android_root}")
    print(f"ROMs: {settings.roms_root}")
    print(f"Recoveries: {settings.recoveries_root}")
    print(f"Tools: {settings.tools_root}")
    print(f"Releases: {settings.releases_root}")
    print(f"Platform: {'Termux' if settings.is_termux else 'Linux'}")
    print(f"Remote host: {settings.remote_host or 'not configured'}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "devices":
        print(format_devices())
        return 0
    if args.command == "config":
        print_config()
        return 0

    settings = load_settings()
    try:
        return run_tui(settings)
    except (curses.error, OSError) as exc:
        print(f"Unable to start the full-screen interface: {exc}", file=sys.stderr)
        print("Try: blinkbox run config", file=sys.stderr)
        return 1
