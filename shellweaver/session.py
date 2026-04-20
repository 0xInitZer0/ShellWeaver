"""
Single web shell session entity.

Owns its NetworkClient, uses ShellDetector to populate context, and is
the only object that knows how to build wrapped commands for CWD tracking.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .config import CWD_SENTINEL
from .detector import ShellDetector
from .exceptions import NetworkError
from .network import NetworkClient


@dataclass
class SessionSnapshot:
    """
    Immutable value object representing a point-in-time view of a session.
    Used by the UI and manager list — never mutated.
    """
    session_id: int
    url: str
    param: str
    method: str
    os_type: str
    shell_type: str
    username: str
    hostname: str
    cwd: str
    label: Optional[str]
    cmd_count: int
    alive: bool = True


class WebShellSession:
    """
    Represents a single remote web shell endpoint and its execution context.

    Responsibilities (SRP):
      - Owns the NetworkClient for transport
      - Delegates environment probing to ShellDetector
      - Tracks CWD across stateless HTTP requests via command wrapping
      - Maintains a per-session command history
    """

    def __init__(
        self,
        session_id: int,
        url: str,
        param: str,
        method: str = "GET",
    ) -> None:
        self.id = session_id
        self.url = url
        self.param = param
        self.method = method.upper()
        self.label: Optional[str] = None
        self.cmd_count: int = 0
        self.history: List[str] = []

        # Remote context — populated by refresh_context()
        self.os_type: str = "Linux"
        self.shell_type: str = "sh"
        self.username: str = "unknown"
        self.hostname: str = "target"
        self.cwd: str = "/"

        self._client = NetworkClient(url, param, method)
        self._detector = ShellDetector(self._client)

        self.refresh_context()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def refresh_context(self) -> None:
        """
        Re-probes the target to update OS, shell, user, hostname, and CWD.
        Safe to call at any time (e.g. after 'cd' or manual refresh).
        """
        self.os_type   = self._detector.detect_os()
        self.shell_type = self._detector.detect_shell(self.os_type)
        self.username  = self._detector.get_whoami()
        self.hostname  = self._detector.get_hostname()
        self.cwd       = self._detector.get_cwd(self.os_type)

    def run_command(self, cmd: str) -> str:
        """
        Execute *cmd* on the remote target in the context of the current CWD.
        Updates self.cwd automatically if the command changes the directory.
        Returns the combined stdout/stderr as a string.
        """
        self.cmd_count += 1
        self.history.append(cmd)

        wrapped = self._build_wrapped(cmd)
        try:
            raw = self._client.execute(wrapped)
        except NetworkError as exc:
            return f"[Network Error] {exc}"

        output, new_cwd = self._parse_raw(raw)
        if new_cwd:
            self.cwd = new_cwd
        return output

    def set_header(self, key: str, value: str) -> None:
        self._client.set_header(key, value)

    def set_cookie(self, key: str, value: str) -> None:
        self._client.set_cookie(key, value)

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            session_id=self.id,
            url=self.url,
            param=self.param,
            method=self.method,
            os_type=self.os_type,
            shell_type=self.shell_type,
            username=self.username,
            hostname=self.hostname,
            cwd=self.cwd,
            label=self.label,
            cmd_count=self.cmd_count,
        )

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _build_wrapped(self, cmd: str) -> str:
        """
        Wrap the user command with:
          1. A `cd` to enforce the current virtual CWD.
          2. The user command itself.
          3. A pwd/cd that prints the new CWD after a unique sentinel.
        This lets us parse the updated CWD out of the single HTTP response.
        """
        if self.os_type == "Windows":
            # cmd.exe: cd /d changes drive+dir; final `cd` prints current path
            return f"cd /d \"{self.cwd}\" & {cmd} & echo {CWD_SENTINEL} & cd"
        else:
            # Unix: use semicolons; echo sentinel then pwd on its own line
            cwd_safe = self.cwd.replace("'", "'\\''")
            return f"cd '{cwd_safe}' 2>/dev/null; {cmd}; echo {CWD_SENTINEL}$(pwd)"

    def _parse_raw(self, raw: str) -> tuple[str, str]:
        """
        Splits *raw* on the CWD_SENTINEL and returns (command_output, new_cwd).
        If the sentinel is absent (e.g. a redirected command), return (raw, '').
        """
        if CWD_SENTINEL not in raw:
            return raw, ""

        parts = raw.split(CWD_SENTINEL, 1)
        output = parts[0].strip()

        cwd_candidate = ""
        if len(parts) > 1:
            cwd_line = parts[1].strip().splitlines()
            if cwd_line:
                cwd_candidate = cwd_line[0].strip()

        return output, cwd_candidate

