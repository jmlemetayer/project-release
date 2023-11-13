"""Config related code."""
import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

import yaml
from pydantic import validate_call
from pydantic import ValidationError

from ._pydantic import UseDefaultValueModel
from .convention import ConventionConfig
from .file import FileConfig
from .git import GitConfig

logger = logging.getLogger(__name__)


class Config(UseDefaultValueModel):
    """Root configuration."""

    convention: ConventionConfig = ConventionConfig()
    file: FileConfig = FileConfig()
    git: GitConfig = GitConfig()


def parse_config(config_file: Path) -> Config:
    """Return the configuration associated with the file.

    Parameters
    ----------
    config_file
        The configuration file to parse.

    Returns
    -------
    Config
        The current configuration object.

    Raises
    ------
    SystemExit
        If the configuration file is invalid or not found.
    """
    if not config_file.exists():
        raise SystemExit("Configuration file not found")
    if not config_file.is_file():
        raise SystemExit("The configuration file is not a regular file")

    try:
        with open(config_file, encoding="utf-8") as stream:
            data = yaml.safe_load(stream) or {}

        @validate_call
        def _parse_config(data: Dict[str, Any]) -> Config:
            return Config(**data)

        return _parse_config(data)

    except (OSError, UnicodeError) as exc:
        raise SystemExit(f"Invalid file: {exc}") from exc

    except yaml.YAMLError as exc:
        lines: List[str] = []
        if hasattr(exc, "problem_mark") and getattr(exc, "problem_mark", None):
            mark = exc.problem_mark
            lines.append(f"at line {mark.line + 1}, column {mark.column + 1}")
        if hasattr(exc, "context") and getattr(exc, "context", None):
            lines.append(str(exc.context))
        if hasattr(exc, "problem") and getattr(exc, "problem", None):
            lines.append(str(exc.problem))
        if lines:
            desc = "syntax error " + ", ".join(lines)
        else:
            desc = str(exc)
        raise SystemExit(f"Invalid yaml file: {desc}") from exc

    except ValidationError as exc:
        raise SystemExit(f"Invalid configuration file: {exc}") from exc
