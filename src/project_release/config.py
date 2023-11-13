"""Config related code."""
import logging
from pathlib import Path
from typing import Any
from typing import Dict

import yaml
from pydantic import ValidationError
from pydantic import validate_call

from ._pydantic import UseDefaultValueModel
from .convention import ConventionConfig
from .error import InvalidConfigFileError
from .error import InvalidUtf8FileError
from .error import InvalidYamlFileError
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
    try:
        with open(config_file, encoding="utf-8") as stream:
            data = yaml.safe_load(stream) or {}

        @validate_call
        def _parse_config(data: Dict[str, Any]) -> Config:
            return Config(**data)

        return _parse_config(data)

    except (OSError, UnicodeError) as exc:
        raise InvalidUtf8FileError(exc) from exc

    except yaml.YAMLError as exc:
        raise InvalidYamlFileError(exc) from exc

    except ValidationError as exc:
        raise InvalidConfigFileError(exc) from exc
