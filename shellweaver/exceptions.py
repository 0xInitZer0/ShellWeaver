"""Custom exception hierarchy for ShellWeaver (ISP / clean error handling)."""


class ShellWeaverError(Exception):
    """Base exception for all ShellWeaver errors."""


class NetworkError(ShellWeaverError):
    """Raised when an HTTP request to the remote target fails."""


class SessionNotFoundError(ShellWeaverError):
    """Raised when a requested session ID does not exist in the manager."""


class InvalidArgumentError(ShellWeaverError):
    """Raised when a command is called with incorrect arguments."""
