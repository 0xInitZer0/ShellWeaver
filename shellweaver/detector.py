"""
Remote OS / shell-type auto-detection.

Follows the Dependency Inversion Principle: depends on the NetworkClient
abstraction, not a concrete transport.
"""
from __future__ import annotations

from .exceptions import NetworkError


class ShellDetector:
    """
    Probes a remote web shell to determine:
      - OS family  (Linux / Windows / macOS)
      - Shell type (bash / zsh / fish / sh / cmd / powershell / …)
      - Running user, hostname, and current working directory
    """

    def __init__(self, client) -> None:
        # Accepts any object that has an .execute(cmd: str) -> str method
        self._client = client

    # ------------------------------------------------------------------ #
    # Public detection methods                                             #
    # ------------------------------------------------------------------ #

    def detect_os(self) -> str:
        """Returns 'Linux', 'macOS', 'Windows', or 'Unknown'."""
        raw = self._probe("uname -s 2>/dev/null || echo WINDOWS")
        low = raw.lower()
        if "linux" in low:
            return "Linux"
        if "darwin" in low:
            return "macOS"
        if "windows" in low or "microsoft" in low:
            return "Windows"
        # Secondary probe: Windows `ver` command
        ver_raw = self._probe("ver")
        if "windows" in ver_raw.lower():
            return "Windows"
        return "Linux"  # safe fallback for unknown Unix systems

    def detect_shell(self, os_type: str = "Linux") -> str:
        """Returns the shell name (bash, zsh, fish, sh, cmd, powershell …)."""
        if os_type == "Windows":
            ps_raw = self._probe("Write-Output ps")
            if ps_raw.strip() == "ps":
                return "powershell"
            return "cmd"

        shell_raw = self._probe("echo $SHELL")
        if shell_raw and "/" in shell_raw:
            return shell_raw.strip().rsplit("/", 1)[-1]

        # Fallback: try $0 which works in most Unix shells
        zero_raw = self._probe("echo $0")
        if zero_raw and zero_raw.strip() not in ("", "$0"):
            name = zero_raw.strip().lstrip("-").rsplit("/", 1)[-1]
            if name:
                return name
        return "sh"

    def get_whoami(self) -> str:
        result = self._probe("whoami")
        return result.splitlines()[0].strip() if result else "unknown"

    def get_hostname(self) -> str:
        result = self._probe("hostname")
        return result.splitlines()[0].strip() if result else "target"

    def get_cwd(self, os_type: str = "Linux") -> str:
        cmd = "cd" if os_type == "Windows" else "pwd"
        result = self._probe(cmd)
        return result.splitlines()[0].strip() if result else ("C:\\inetpub\\wwwroot" if os_type == "Windows" else "/")

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _probe(self, cmd: str) -> str:
        try:
            return self._client.execute(cmd).strip()
        except NetworkError:
            return ""
        except Exception:
            return ""
