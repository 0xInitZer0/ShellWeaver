"""
Session lifecycle manager — the Application Service layer.

Owns the collection of WebShellSessions and exposes clean CRUD operations.
Follows SRP (only manages sessions) and OCP (sessions are pluggable entities).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .exceptions import SessionNotFoundError
from .session import SessionSnapshot, WebShellSession


class SessionManager:
    """
    Create, retrieve, enumerate, rename, and destroy WebShellSessions.
    No network or UI logic lives here.
    """

    def __init__(self) -> None:
        self._sessions: Dict[int, WebShellSession] = {}
        self._counter: int = 1

    # ------------------------------------------------------------------ #
    # Mutation                                                             #
    # ------------------------------------------------------------------ #

    def add_session(self, url: str, param: str, method: str = "GET") -> WebShellSession:
        """Create a new session, probe the target, and register it."""
        session = WebShellSession(self._counter, url, param, method)
        self._sessions[self._counter] = session
        self._counter += 1
        return session

    def kill_session(self, session_id: int) -> None:
        """Remove a session by ID. Raises SessionNotFoundError if absent."""
        self._require(session_id)
        del self._sessions[session_id]

    def rename_session(self, session_id: int, label: str) -> None:
        """Attach a human-readable label to a session."""
        self._require(session_id).label = label.strip()

    # ------------------------------------------------------------------ #
    # Query                                                                #
    # ------------------------------------------------------------------ #

    def get_session(self, session_id: int) -> WebShellSession:
        """Return the live session object. Raises SessionNotFoundError if absent."""
        return self._require(session_id)

    def list_snapshots(self) -> List[SessionSnapshot]:
        """Return immutable point-in-time snapshots of all sessions (safe for UI)."""
        return [s.snapshot() for s in self._sessions.values()]

    def count(self) -> int:
        return len(self._sessions)

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _require(self, session_id: int) -> WebShellSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(
                f"Session [bold yellow]{session_id}[/bold yellow] not found. "
                f"Use [cyan]list[/cyan] to see active sessions."
            )
        return session

