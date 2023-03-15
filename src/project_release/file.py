"""Files related code."""
import logging
import re
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import List
from typing import Union

logger = logging.getLogger(__name__)


class NoVersionFoundError(Exception):
    """No version has been found."""


class EmptyVersionError(Exception):
    """An empty version has been found."""


class InconsistentVersionError(Exception):
    """Multiple inconsistent versions has been found."""


class VersionFile(ABC):
    """An abstract class to handle a version file."""

    _path: Union[Path, str]

    @property
    @abstractmethod
    def versions(self) -> List[str]:
        """str: All the versions related to the file."""
        raise NotImplementedError

    @property
    def version(self) -> str:
        """str: The version related to the file.

        Raises
        ------
        NoVersionFoundError
            If no version has been found.
        EmptyVersionError
            If an empty version has been found.
        InconsistentVersionError
            If multiple inconsistent versions has been found.
        """
        versions = self.versions
        if not versions:
            raise NoVersionFoundError(f"No version found in file: {self._path}")
        if not all(version == versions[0] for version in versions):
            raise InconsistentVersionError(
                f"Inconsistent version found in file: {self._path}: {versions}"
            )
        if versions[0] == "":
            raise EmptyVersionError(f"No version found in file: {self._path}")
        return versions[0]

    @version.setter
    def version(self, version: str) -> None:
        self._set_version(version)

    @abstractmethod
    def _set_version(self, version: str) -> None:
        raise NotImplementedError


class PlainVersionFile(VersionFile):
    """Plain version file."""

    def __init__(self, path: Union[Path, str]) -> None:
        self._path = path

    @property
    def versions(self) -> List[str]:
        """str: All the versions related to the file."""
        with open(self._path, encoding="utf-8") as stream:
            version = stream.read()
        return [version]

    def _set_version(self, version: str) -> None:
        with open(self._path, "w", encoding="utf-8") as stream:
            stream.write(version)


class FormattedVersionFile(VersionFile):
    """Formatted version file."""

    def __init__(self, path: Union[Path, str], f0rmat: str) -> None:
        self._path = path
        self.__f0rmat = f0rmat
        self.__pattern = f0rmat % {"version": "(.*)"}

    @property
    def versions(self) -> List[str]:
        """str: All the versions related to the file."""
        with open(self._path, encoding="utf-8") as stream:
            data = stream.read()
        match = re.search(self.__pattern, data)
        if match is None:
            return []
        return list(match.groups())

    def _set_version(self, version: str) -> None:
        with open(self._path, "w", encoding="utf-8") as stream:
            stream.write(self.__f0rmat % {"version": version})


class EditedVersionFile(VersionFile):
    """Edited version file."""

    def __init__(self, path: Union[Path, str], pattern: str) -> None:
        self._path = path
        self.__patern = pattern

    @property
    def versions(self) -> List[str]:
        """str: All the versions related to the file."""
        with open(self._path, encoding="utf-8") as stream:
            return re.findall(self.__patern, stream.read())

    def _set_version(self, version: str) -> None:
        with open(self._path, "r+", encoding="utf-8") as stream:
            data = stream.read()
            stream.seek(0)
            stream.write(re.sub(self.__patern, version, data))
