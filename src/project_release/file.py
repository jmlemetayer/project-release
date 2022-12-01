"""Files related code."""
import logging
import re
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


class NoVersionFoundError(Exception):
    """No version has been found."""


class EmptyVersionError(Exception):
    """An empty version has been found."""


class InconsistentVersionError(Exception):
    """Multiple inconsistent versions has been found."""


class VersionFile(ABC):  # pylint: disable=too-few-public-methods
    """An abstract class to handle a version file."""

    @property
    @abstractmethod
    def version(self) -> str:
        """str: The version related to the file."""
        raise NotImplementedError

    @version.setter
    @abstractmethod
    def version(self, version: str) -> None:
        raise NotImplementedError


class PlainVersionFile(VersionFile):  # pylint: disable=too-few-public-methods
    """Plain version file."""

    def __init__(self, path: Union[Path, str]) -> None:
        self.__path = path

    @property
    def version(self) -> str:
        """str: The version related to the file.

        Raises
        ------
        NoVersionFoundError
            If no version has been found.
        """
        with open(self.__path, encoding="utf-8") as stream:
            version = stream.read()
        if version == "":
            raise NoVersionFoundError(f"No version found in file: {self.__path}")
        return version

    @version.setter
    def version(self, version: str) -> None:
        with open(self.__path, "w", encoding="utf-8") as stream:
            stream.write(version)


class FormattedVersionFile(VersionFile):  # pylint: disable=too-few-public-methods
    """Formatted version file."""

    def __init__(self, path: Union[Path, str], f0rmat: str) -> None:
        self.__path = path
        self.__f0rmat = f0rmat
        self.__pattern = f0rmat % {"version": "(.*)"}

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
        with open(self.__path, encoding="utf-8") as stream:
            data = stream.read()
        match = re.search(self.__pattern, data)
        if match is None:
            raise NoVersionFoundError(f"No version found in file: {self.__path}")
        versions = match.groups()
        if not all(version == versions[0] for version in versions):
            raise InconsistentVersionError(
                f"Inconsistent version found in file: {self.__path}: {versions}"
            )
        if versions[0] == "":
            raise EmptyVersionError(f"No version found in file: {self.__path}")
        return versions[0]

    @version.setter
    def version(self, version: str) -> None:
        with open(self.__path, "w", encoding="utf-8") as stream:
            stream.write(self.__f0rmat % {"version": version})


class EditedVersionFile(VersionFile):  # pylint: disable=too-few-public-methods
    """Edited version file."""

    def __init__(self, path: Union[Path, str], pattern: str) -> None:
        self.__path = path
        self.__patern = pattern

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
        with open(self.__path, encoding="utf-8") as stream:
            versions = re.findall(self.__patern, stream.read())
        if len(versions) == 0:
            raise NoVersionFoundError(f"No version found in file: {self.__path}")
        if not all(version == versions[0] for version in versions):
            raise InconsistentVersionError(
                f"Inconsistent version found in file: {self.__path}: {versions}"
            )
        if versions[0] == "":
            raise EmptyVersionError(f"No version found in file: {self.__path}")
        return versions[0]

    @version.setter
    def version(self, version: str) -> None:
        with open(self.__path, "r+", encoding="utf-8") as stream:
            data = stream.read()
            stream.seek(0)
            stream.write(re.sub(self.__patern, version, data))
