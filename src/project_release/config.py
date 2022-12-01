"""Config related code."""
import logging
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import yaml

from .convention import Pep440Convention
from .convention import SemverConvention
from .convention import VersionConvention
from .file import EditedVersionFile
from .file import FormattedVersionFile
from .file import PlainVersionFile
from .file import VersionFile

logger = logging.getLogger(__name__)


class ConventionConfig:  # pylint: disable=too-few-public-methods
    """A class to handle the convention config."""

    def __init__(self) -> None:
        self.version: Optional[VersionConvention] = None


class FileConfig:  # pylint: disable=too-few-public-methods
    """A class to handle the file config."""

    def __init__(self) -> None:
        self.version: List[VersionFile] = []


class Config:  # pylint: disable=too-few-public-methods
    """A class to handle the config file."""

    def __init__(self, path: Union[Path, str]) -> None:
        self.__path = path
        self.convention = ConventionConfig()
        self.file = FileConfig()

    def __parse_convention(self, data: Any) -> None:
        """Parse the 'convention' dictionary."""
        convention = data.get("convention")
        if convention is None:
            return

        version = convention.get("version")
        if version is None:
            return

        if version == "semver":
            self.convention.version = SemverConvention()
        elif version == "pep440":
            self.convention.version = Pep440Convention()
        else:
            raise ValueError("Invalid value in 'convention.version'")

    def __parse_file_version_item(self, data: Any) -> None:
        """Parse the 'file.version' item."""
        if isinstance(data, str):
            return self.file.version.append(PlainVersionFile(data))

        if not isinstance(data, dict):
            raise TypeError("Invalid type for: 'file.version'")

        path = data.get("path")
        f0rmat = data.get("format")
        pattern = data.get("pattern")

        if path is None:
            raise ValueError("Missing 'path' value in 'file.version'")

        if not isinstance(path, str):
            raise TypeError("Invalid 'path' type in 'file.version'")

        if f0rmat is None and pattern is None:
            return self.file.version.append(PlainVersionFile(path))
        if f0rmat is not None and pattern is None:
            if not isinstance(f0rmat, str):
                raise TypeError("Invalid 'format' type in 'file.version'")
            return self.file.version.append(FormattedVersionFile(path, f0rmat))
        if f0rmat is None and pattern is not None:
            if not isinstance(pattern, str):
                raise TypeError("Invalid 'pattern' type in 'file.version'")
            return self.file.version.append(EditedVersionFile(path, pattern))
        raise ValueError("Both existing 'format' and 'pattern' in 'file.version'")

    def __parse_file(self, data: Any) -> None:
        """Parse the 'file' dictionary."""
        file = data.get("file")
        if file is None:
            return

        versions = file.get("version")
        if versions is None:
            return

        if isinstance(versions, list):
            for version in versions:
                self.__parse_file_version_item(version)
        else:
            self.__parse_file_version_item(versions)

    def parse(self) -> None:
        """Parse the config file.

        Raises
        ------
        yaml.YAMLError
            If the yaml is invalid.
        ValueError
            If a value is invalid.
        TypeError
            If the type of a value is invalid.
        """
        with open(self.__path, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        self.__parse_convention(data)
        self.__parse_file(data)
