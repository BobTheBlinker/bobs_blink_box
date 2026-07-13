from __future__ import annotations

import curses
import textwrap

from blinkbox.config import Settings
from blinkbox.tools.device import format_devices
from blinkbox.ui.logo import COMPACT_LOGO, LOGO

MENU = ("HOME", "INSTALL", "SYNC", "BUILD", "TOOLS", "RELEASES", "SETTINGS", "ABOUT")

PAGE_TEXT = {
    "HOME": "Headless-first Android building and device toolbox. Linux, SSH, and Termux are first-class targets.",
    "INSTALL": "Install, update, repair, and remove toolbox-managed components. The Android workspace is never removed automatically.",
    "SYNC": "ROM, recovery, manifest, device-tree, kernel, and vendor synchronization will live here.",
    "BUILD": "ROM and recovery build orchestration will live here. Source trees remain under ~/Android.",
    "TOOLS": "Device scanner is active. Copy Partitions A → B is the next major tool and remains disabled until its safety checks are complete.",
    "RELEASES": "Finished ZIPs, images, checksums, and release notes will be organized under ~/Android/Releases.",
    "SETTINGS": "User-adjustable identity and path settings come from blinkbox.sh, keeping the Python package generic.",
    "ABOUT": "Bob's Blink Box v0.1.0. Built for terminals first, shiny windows later.",
}


def _safe_addstr(window: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
    height, width = window.getmaxyx()
    if y < 0 or y >= height or x >= width:
        return
    clipped = text[: max(0, width - x - 1)]
    try:
        window.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def _center(window: curses.window, y: int, text: str, attr: int = 0) -> None:
    _, width = window.getmaxyx()
    _safe_addstr(window, y, max(0, (width - len(text)) // 2), text, attr)


def _draw_menu(window: curses.window, selected: int, y: int) -> int:
    _, width = window.getmaxyx()
    labels = [f" {name} " for name in MENU]
    total = sum(len(label) for label in labels) + len(labels) - 1

    if total < width:
        x = max(0, (width - total) // 2)
        for index, label in enumerate(labels):
            attr = curses.A_REVERSE | curses.A_BOLD if index == selected else curses.A_NORMAL
            _safe_addstr(window, y, x, label, attr)
            x += len(label) + 1
        return y + 2

    x = 1
    row = y
    for index, label in enumerate(labels):
        if x + len(label) >= width:
            row += 1
            x = 1
        attr = curses.A_REVERSE | curses.A_BOLD if index == selected else curses.A_NORMAL
        _safe_addstr(window, row, x, label, attr)
        x += len(label) + 1
    return row + 2


def _draw_logo(window: curses.window, start_y: int) -> int:
    _, width = window.getmaxyx()
    logo = LOGO if width >= max(map(len, LOGO)) + 2 else COMPACT_LOGO
    for offset, line in enumerate(logo):
        _center(window, start_y + offset, line, curses.A_BOLD)
    return start_y + len(logo) + 1


def _draw_page(window: curses.window, settings: Settings, selected: int) -> None:
    height, width = window.getmaxyx()
    window.erase()
    page = MENU[selected]

    if page == "HOME":
        y = _draw_logo(window, 1)
        y = _draw_menu(window, selected, y)
    else:
        y = _draw_menu(window, selected, 0)
        _center(window, y, page, curses.A_BOLD | curses.A_UNDERLINE)
        y += 2

    body_width = max(20, width - 4)
    text = PAGE_TEXT[page]
    if page == "TOOLS":
        text += "\n\nConnected devices:\n" + format_devices()
    elif page == "SETTINGS":
        text += (
            f"\n\nMaintainer: {settings.maintainer_name}"
            f"\nAndroid root: {settings.android_root}"
            f"\nROMs: {settings.roms_root}"
            f"\nRecoveries: {settings.recoveries_root}"
            f"\nTools: {settings.tools_root}"
            f"\nReleases: {settings.releases_root}"
            f"\nPlatform: {'Termux' if settings.is_termux else 'Linux'}"
            f"\nRemote host: {settings.remote_host or 'not configured'}"
        )

    for paragraph in text.splitlines():
        lines = textwrap.wrap(paragraph, body_width) or [""]
        for line in lines:
            if y >= height - 2:
                break
            _safe_addstr(window, y, 2, line)
            y += 1

    _safe_addstr(window, height - 1, 1, "←/→ menu  Enter select  r refresh  q quit", curses.A_DIM)
    window.refresh()


def run_tui(settings: Settings) -> int:
    def _main(window: curses.window) -> int:
        curses.curs_set(0)
        window.keypad(True)
        selected = 0

        while True:
            _draw_page(window, settings, selected)
            key = window.getch()
            if key in (ord("q"), 27):
                return 0
            if key in (curses.KEY_LEFT, ord("h")):
                selected = (selected - 1) % len(MENU)
            elif key in (curses.KEY_RIGHT, ord("l"), 9):
                selected = (selected + 1) % len(MENU)
            elif key in (curses.KEY_RESIZE, ord("r"), 10, 13, curses.KEY_ENTER):
                continue

    return curses.wrapper(_main)
