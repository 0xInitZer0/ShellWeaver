"""
All terminal rendering — the only module that calls rich directly (SRP).

Nothing in this module makes network calls or holds business logic.
"""
from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import APP_NAME, VERSION

# ── ASCII banner ──────────────────────────────────────────────────────────────
_BANNER = r"""
   ____  _          _ ___       __
  / ___|| |__   ___| |/ \ \    / /__  __ ___   _____ _ __
  \___ \| '_ \ / _ \ | |\ \ /\ / / _ \/ _` \ \ / / _ \ '__|
   ___) | | | |  __/ | | \ V  V /  __/ (_| |\ V /  __/ |
  |____/|_| |_|\___|_|_|  \_/\_/ \___|\__,_| \_/ \___|_|
"""


class UI:
    """Renders all output to the terminal. No business logic."""

    def __init__(self) -> None:
        self.console = Console()

    # ── Banner ────────────────────────────────────────────────────────────────

    def print_banner(self) -> None:
        banner = Text(_BANNER, style="bold cyan", justify="center")
        subtitle = (
            f"[bold white]v{VERSION}[/bold white]  "
            "[dim]·[/dim]  "
            "[dim]CTF Web Shell Manager[/dim]"
        )
        self.console.print(
            Panel(
                banner,
                subtitle=subtitle,
                border_style="bright_cyan",
                expand=True,
                padding=(0, 2),
            )
        )
        self.console.print()

    # ── Status messages ───────────────────────────────────────────────────────

    def print_error(self, msg: str) -> None:
        self.console.print(f"  [bold red]✗[/bold red]  {msg}")

    def print_success(self, msg: str) -> None:
        self.console.print(f"  [bold green]✔[/bold green]  {msg}")

    def print_info(self, msg: str) -> None:
        self.console.print(f"  [bold bright_blue]ℹ[/bold bright_blue]  {msg}")

    def print_warning(self, msg: str) -> None:
        self.console.print(f"  [bold yellow]⚠[/bold yellow]  {msg}")

    def print_output(self, output: str) -> None:
        """Print raw command output with subtle white styling."""
        if output:
            self.console.print(output, style="bright_white", highlight=False)

    # ── Sessions table ────────────────────────────────────────────────────────

    def print_sessions_table(self, snapshots: list) -> None:
        if not snapshots:
            self.print_info(
                "No active sessions. Use [cyan]add <url> <param>[/cyan] to open one."
            )
            return

        table = Table(
            title="[bold cyan]Active Sessions[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold magenta",
            show_lines=True,
            title_justify="left",
        )
        table.add_column("ID",     style="bold yellow",  justify="center", width=4)
        table.add_column("Label",  style="cyan",          width=14)
        table.add_column("URL",    style="white",         no_wrap=True)
        table.add_column("Param",  style="green",         width=8)
        table.add_column("Method", style="yellow",        width=7)
        table.add_column("OS",     style="bright_blue",   width=8)
        table.add_column("Shell",  style="magenta",       width=12)
        table.add_column("User",   style="bold green",    width=14)
        table.add_column("CWD",    style="dim white")

        for s in snapshots:
            os_icon = {"Linux": "🐧", "Windows": "🪟", "macOS": "🍎"}.get(s.os_type, "❓")
            label = s.label or "[dim]-[/dim]"
            table.add_row(
                str(s.session_id),
                label,
                s.url,
                s.param,
                s.method,
                f"{os_icon} {s.os_type}",
                s.shell_type,
                s.username,
                s.cwd,
            )

        self.console.print(table)

    # ── Session detail panel ──────────────────────────────────────────────────

    def print_session_detail(self, snap) -> None:
        rows = [
            ("ID",           str(snap.session_id)),
            ("Label",        snap.label or "[dim]-[/dim]"),
            ("URL",          snap.url),
            ("Parameter",    snap.param),
            ("Method",       snap.method),
            ("OS",           snap.os_type),
            ("Shell",        snap.shell_type),
            ("User",         snap.username),
            ("Hostname",     snap.hostname),
            ("Directory",    snap.cwd),
            ("Commands run", str(snap.cmd_count)),
        ]
        tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tbl.add_column("key",   style="bold cyan",  no_wrap=True)
        tbl.add_column("value", style="bright_white")
        for k, v in rows:
            tbl.add_row(k, v)
        self.console.print(
            Panel(
                tbl,
                title=f"[bold cyan]Session {snap.session_id}[/bold cyan]",
                border_style="cyan",
            )
        )

    # ── Help ──────────────────────────────────────────────────────────────────

    def print_help(self) -> None:
        # ── Main commands ──
        main_tbl = Table(
            box=box.SIMPLE, show_header=True,
            header_style="bold cyan", padding=(0, 2),
        )
        main_tbl.add_column("Command",     style="bold yellow", no_wrap=True)
        main_tbl.add_column("Description", style="white")
        main_tbl.add_column("Example",     style="dim")

        main_cmds = [
            ("add <url> <param> [method]",   "Add a web shell session (GET default)", "add http://10.0.0.5/sh.php cmd POST"),
            ("list",                          "Show all active sessions",              "list"),
            ("fg <id>",                       "Interact with session",                 "fg 1"),
            ("info <id>",                     "Detailed session info",                 "info 2"),
            ("rename <id> <label>",           "Label a session",                       "rename 1 admin-panel"),
            ("header <id> <key> <value>",     "Set custom HTTP header",                "header 1 X-Forwarded-For 127.0.0.1"),
            ("cookie <id> <key> <value>",     "Set a request cookie",                  "cookie 1 PHPSESSID abc123"),
            ("kill <id>",                     "Terminate and remove session",          "kill 3"),
            ("help",                          "Show this help screen",                 "help"),
            ("exit / quit",                   "Exit ShellWeaver",                      "exit"),
        ]
        for cmd, desc, ex in main_cmds:
            main_tbl.add_row(cmd, desc, ex)

        self.console.print(
            Panel(
                main_tbl,
                title="[bold cyan]Main Prompt Commands[/bold cyan]",
                border_style="bright_cyan",
            )
        )

        # ── Interactive session commands ──
        sess_tbl = Table(
            box=box.SIMPLE, show_header=True,
            header_style="bold cyan", padding=(0, 2),
        )
        sess_tbl.add_column("Command",     style="bold yellow", no_wrap=True)
        sess_tbl.add_column("Description", style="white")
        sess_cmds = [
            ("bg",          "Background this session, return to Weaver"),
            ("exit",        "Kill session and return to Weaver"),
            ("info",        "Print current session context"),
            ("refresh",     "Re-probe whoami / hostname / cwd"),
            ("history",     "Show command history for this session"),
            ("<any cmd>",   "Execute on the remote target"),
        ]
        for cmd, desc in sess_cmds:
            sess_tbl.add_row(cmd, desc)

        self.console.print(
            Panel(
                sess_tbl,
                title="[bold cyan]Interactive Session Commands[/bold cyan]",
                border_style="bright_cyan",
            )
        )


# Module-level singleton — import `ui` everywhere
ui = UI()

