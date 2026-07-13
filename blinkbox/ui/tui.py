from __future__ import annotations

import curses
from dataclasses import dataclass
from typing import Callable

from blinkbox import __version__
from blinkbox.config import UserConfig
from blinkbox.tools.device import scan_devices, tool_status
from blinkbox.ui.logo import LOGO


@dataclass(frozen=True)
class Page:
    title: str
    draw: Callable[["BlinkBoxTUI", int, int, int], None]


class BlinkBoxTUI:
    def __init__(self, screen: "curses._CursesWindow", config: UserConfig) -> None:
        self.screen = screen
        self.config = config
        self.selected = 0
        self.active = 0
        self.status = "Arrow keys move. Enter opens. Esc returns home. Q quits."
        self.pages = [
            Page("HOME", BlinkBoxTUI.draw_home),
            Page("INSTALL", BlinkBoxTUI.draw_install),
            Page("SYNC", BlinkBoxTUI.draw_sync),
            Page("BUILD", BlinkBoxTUI.draw_build),
            Page("TOOLS", BlinkBoxTUI.draw_tools),
            Page("RELEASES", BlinkBoxTUI.draw_releases),
            Page("SETTINGS", BlinkBoxTUI.draw_settings),
            Page("ABOUT", BlinkBoxTUI.draw_about),
        ]

    def run(self) -> None:
        curses.curs_set(0)
        self.screen.keypad(True)
        self.screen.timeout(-1)

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)

        while True:
            self.draw()
            key = self.screen.getch()
            if key in (ord("q"), ord("Q")):
                return
            if key in (curses.KEY_LEFT, ord("h"), ord("H")):
                self.selected = (self.selected - 1) % len(self.pages)
            elif key in (curses.KEY_RIGHT, ord("l"), ord("L"), 9):
                self.selected = (self.selected + 1) % len(self.pages)
            elif key in (10, 13, curses.KEY_ENTER):
                self.active = self.selected
            elif key in (27, curses.KEY_BACKSPACE, 127):
                self.active = 0
                self.selected = 0
            elif key == curses.KEY_RESIZE:
                continue
            elif key in (ord("r"), ord("R")) and self.pages[self.active].title == "TOOLS":
                self.status = self.device_summary()

    def dimensions(self) -> tuple[int, int, int]:
        rows, cols = self.screen.getmaxyx()
        if cols > rows and cols >= 80:
            width = max(44, cols // 2)
        else:
            width = cols
        return rows, cols, min(width, cols)

    def safe_add(self, y: int, x: int, text: str, attr: int = 0, width: int | None = None) -> None:
        rows, cols = self.screen.getmaxyx()
        if y < 0 or y >= rows or x < 0 or x >= cols:
            return
        allowed = cols - x - 1
        if width is not None:
            allowed = min(allowed, width)
        if allowed <= 0:
            return
        try:
            self.screen.addnstr(y, x, text, allowed, attr)
        except curses.error:
            pass

    def draw(self) -> None:
        self.screen.erase()
        rows, _, width = self.dimensions()
        if rows < 12 or width < 32:
            self.safe_add(0, 0, "Terminal too small. Rotate or enlarge it.", curses.A_BOLD)
            self.safe_add(2, 0, f"Current usable area: {width}x{rows}")
            self.safe_add(rows - 1, 0, "Q quits")
            self.screen.refresh()
            return

        if self.active == 0:
            self.draw_home_screen(rows, width)
        else:
            body_top = self.draw_top_menu(width)
            self.pages[self.active].draw(self, body_top, rows, width)

        self.draw_footer(rows, width)
        self.screen.refresh()

    def draw_home_screen(self, rows: int, width: int) -> None:
        logo_width = max(len(line) for line in LOGO)
        if width >= logo_width + 2 and rows >= len(LOGO) + 8:
            y = 1
            x = max(0, (width - logo_width) // 2)
            for line in LOGO:
                self.safe_add(y, x, line, curses.color_pair(1) | curses.A_BOLD, width - x)
                y += 1
            self.safe_add(y + 1, 2, f"Maintainer: {self.config.maintainer_name}", curses.A_BOLD)
            self.safe_add(y + 2, 2, f"Blink Box v{__version__}")
            menu_y = y + 4
        else:
            self.safe_add(1, 2, "BOB'S BLINK BOX", curses.color_pair(1) | curses.A_BOLD)
            self.safe_add(2, 2, f"Maintainer: {self.config.maintainer_name}")
            menu_y = 4

        self.draw_menu(menu_y, width)
        self.safe_add(menu_y + 3, 2, "Select a section and press Enter.")

    def draw_top_menu(self, width: int) -> int:
        self.draw_menu(0, width)
        self.safe_add(2, 0, "─" * max(0, width - 1))
        return 4

    def draw_menu(self, y: int, width: int) -> None:
        labels = [page.title for page in self.pages]
        total = sum(len(label) + 3 for label in labels)

        if total <= width - 2:
            x = 1
            for index, label in enumerate(labels):
                text = f" {label} "
                attr = curses.color_pair(2) | curses.A_BOLD if index == self.selected else curses.A_BOLD
                self.safe_add(y, x, text, attr)
                x += len(text) + 1
            return

        # Narrow phone layout: show a compact three-item carousel.
        previous_index = (self.selected - 1) % len(labels)
        next_index = (self.selected + 1) % len(labels)
        compact = f"‹ {labels[previous_index]}   [ {labels[self.selected]} ]   {labels[next_index]} ›"
        x = max(0, (width - len(compact)) // 2)
        self.safe_add(y, x, compact, curses.color_pair(1) | curses.A_BOLD, width - x)

    def draw_footer(self, rows: int, width: int) -> None:
        self.safe_add(rows - 2, 0, "─" * max(0, width - 1))
        self.safe_add(rows - 1, 1, self.status, curses.color_pair(3), width - 2)

    def heading(self, y: int, title: str) -> int:
        self.safe_add(y, 2, title, curses.color_pair(1) | curses.A_BOLD)
        return y + 2

    def lines(self, y: int, lines: list[str], width: int) -> None:
        for line in lines:
            self.safe_add(y, 4, line, width=width - 6)
            y += 1

    def draw_home(self, y: int, rows: int, width: int) -> None:
        del y, rows, width

    def draw_install(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "INSTALL")
        self.lines(y, [
            "Application installation and repair live in launcher.sh.",
            "Commands: install, update, repair, uninstall, and nuke.",
            "Your ~/Android workspace is preserved during normal uninstall.",
        ], width)

    def draw_sync(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "SYNC")
        self.lines(y, [
            "Repository and manifest synchronization will live here.",
            "The implementation will remain usable from SSH and Termux.",
        ], width)

    def draw_build(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "BUILD")
        self.lines(y, [
            f"Android root: {self.config.android_root}",
            f"ROM sources: {self.config.roms_root}",
            f"Recovery sources: {self.config.recoveries_root}",
            "Each source tree keeps its own build output directory.",
        ], width)

    def draw_tools(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "TOOLS")
        self.lines(y, [
            f"Tool storage: {self.config.tools_root}",
            "",
            "R  Refresh connected-device status",
            "",
            *tool_status(),
            "",
            self.device_summary(),
            "",
            "Planned: Copy A-slot partitions to B-slot partitions.",
        ], width)

    def draw_releases(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "RELEASES")
        self.lines(y, [
            f"Release root: {self.config.releases_root}",
            "Packaging, checksums, and release indexing will live here.",
        ], width)

    def draw_settings(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "SETTINGS")
        self.lines(y, [
            f"Maintainer:  {self.config.maintainer_name}",
            f"Git user:    {self.config.git_username}",
            f"Git email:   {self.config.git_email}",
            f"Editor:      {self.config.editor}",
            f"Remote host: {self.config.remote_host or 'not configured'}",
            "",
            "Edit frequently changed values near the top of launcher.sh.",
        ], width)

    def draw_about(self, y: int, rows: int, width: int) -> None:
        del rows
        y = self.heading(y, "ABOUT")
        self.lines(y, [
            f"Bob's Blink Box v{__version__}",
            "Headless-first Android build and device toolbox.",
            "Targets: Linux, SSH sessions, and Termux.",
        ], width)

    @staticmethod
    def device_summary() -> str:
        try:
            devices = scan_devices()
        except Exception as exc:  # Defensive UI boundary.
            return f"Device scan failed: {exc}"
        if not devices:
            return "No ADB or fastboot devices detected."
        return " | ".join(f"{d.transport}:{d.serial} ({d.state})" for d in devices)
