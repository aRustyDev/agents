"""Custom exceptions for skill-pr-addresser."""


class AddresserError(Exception):
    """Base exception for skill-pr-addresser."""

    exit_code = 1


class PRNotFoundError(AddresserError):
    """PR does not exist."""

    pass


class PRClosedError(AddresserError):
    """PR is already merged or closed."""

    exit_code = 0  # Not an error - just nothing to do


class NoFeedbackError(AddresserError):
    """No feedback to address."""

    exit_code = 0  # Not an error - just nothing to do


class WorktreeError(AddresserError):
    """Worktree operation failed."""

    pass


class ConflictError(AddresserError):
    """Git conflict detected."""

    pass


class IterationLimitError(AddresserError):
    """Max iterations reached without approval."""

    pass


class SessionNotFoundError(AddresserError):
    """Session not found."""

    pass


class RateLimitError(AddresserError):
    """API rate limit exceeded."""

    pass
