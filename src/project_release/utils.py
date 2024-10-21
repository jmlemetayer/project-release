"""Simple utility functions."""

import logging
from pathlib import Path
from typing import Union

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


def relative_path(path: Union[Path, str]) -> Path:
    """Get the relative path from the current directory if possible."""
    if not isinstance(path, Path):
        path = Path(path)
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path
