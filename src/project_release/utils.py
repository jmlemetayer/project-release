"""Simple utility functions."""
import logging

logger = logging.getLogger(__name__)


def log_exception(exc: BaseException, level: int = logging.ERROR) -> None:
    """Log exception recursively.

    Parameters
    ----------
    exc
        The exception to log.
    level
        An optional logging level.
    """
    if exc.__cause__:
        log_exception(exc.__cause__, level)
    logger.log(level, str(exc))
