"""Config related code."""
import logging
import os
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import TextIO

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

CONFIG_FILE = ".project-release-config.yaml"
CONFIG_HELP = "See https://project-release.readthedocs.io for more information"


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
        logger.debug(f"parsing config file: {config_file}")

        with open(config_file, encoding="utf-8") as stream:
            data = yaml.safe_load(stream) or {}

        @validate_call
        def _parse_config(data: Dict[str, Any]) -> Config:
            return Config(**data)

        config = _parse_config(data)
        logger.debug(f"parsed config: {config}")
        return config

    except (OSError, UnicodeError) as exc:
        raise InvalidUtf8FileError(exc) from exc

    except yaml.YAMLError as exc:
        raise InvalidYamlFileError(exc) from exc

    except ValidationError as exc:
        raise InvalidConfigFileError(exc) from exc


def dump_config(config: Config, stream: TextIO = sys.stdout) -> None:
    """Dump a configuration object.

    Parameters
    ----------
    config
        The configuration object to print.
    stream
        The output stream (default: ``sys.stdout``).
    """
    stream.write(f"# {CONFIG_HELP}{os.linesep}")
    yaml.safe_dump(
        config.model_dump(by_alias=True),
        stream,
        default_flow_style=False,
        line_break=os.linesep,
    )


def sample_config(stream: TextIO = sys.stdout) -> None:
    """Dump a sample configuration.

    Parameters
    ----------
    stream
        The output stream (default: ``sys.stdout``).
    """
    dump_config(Config())
