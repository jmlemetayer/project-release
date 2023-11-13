"""Files related code."""
import logging
import re
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import field_validator
from pydantic import model_serializer
from pydantic import validate_call

from ._pydantic import Listable
from ._pydantic import UseDefaultValueModel
from .error import VersionEmptyError
from .error import VersionInconsistentError
from .error import VersionNotFoundError

logger = logging.getLogger(__name__)


class VersionFile(ABC, BaseModel):
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
        VersionNotFoundError
            If no version has been found.
        VersionEmptyError
            If an empty version has been found.
        VersionInconsistentError
            If multiple inconsistent versions has been found.
        """
        versions = self.versions
        if not versions:
            raise VersionNotFoundError(self._path)
        if not all(version == versions[0] for version in versions):
            raise VersionInconsistentError(self._path, versions)
        if versions[0] == "":
            raise VersionEmptyError(self._path)
        return versions[0]

    @version.setter
    def version(self, version: str) -> None:
        self._set_version(version)

    @abstractmethod
    def _set_version(self, version: str) -> None:
        raise NotImplementedError

    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Generate a dictionary representation of the model."""
        return self._serialize()

    @abstractmethod
    def _serialize(self) -> Dict[str, Any]:
        raise NotImplementedError


class PlainVersionFile(VersionFile):
    """Plain version file."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__()
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

    def _serialize(self) -> Dict[str, Any]:
        return {"path": self._path}


class FormattedVersionFile(VersionFile):
    """Formatted version file."""

    def __init__(self, path: Union[Path, str], fromat: str) -> None:
        super().__init__()
        self._path = path
        self.__fromat = fromat
        self.__pattern = fromat % {"version": "(.*)"}

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
            stream.write(self.__fromat % {"version": version})

    def _serialize(self) -> Dict[str, Any]:
        return {"path": self._path, "format": self.__fromat}


class EditedVersionFile(VersionFile):
    """Edited version file."""

    def __init__(self, path: Union[Path, str], pattern: str) -> None:
        super().__init__()
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

    def _serialize(self) -> Dict[str, Any]:
        return {"path": self._path, "pattern": self.__patern}


VersionConfigType = Union[str, Dict[str, str]]


class FileConfig(UseDefaultValueModel):
    """File configuration."""

    version: List[VersionFile] = []  # noqa: RUF012

    @field_validator("version", mode="before")
    @classmethod
    @validate_call
    def _validate_version(
        cls, value: Optional[Listable[VersionConfigType]]
    ) -> List[VersionFile]:
        @validate_call
        def parse_version_file(value: VersionConfigType) -> VersionFile:
            if isinstance(value, str):
                return PlainVersionFile(value)
            if "path" not in value:
                raise ValueError("version file must contain a path")
            if "format" in value and "pattern" in value:
                raise ValueError("format and pattern fields are exclusive")
            if "format" in value:
                return FormattedVersionFile(value["path"], value["format"])
            if "pattern" in value:
                return EditedVersionFile(value["path"], value["pattern"])
            return PlainVersionFile(value["path"])

        if value is None:
            return []
        if isinstance(value, list):
            return [parse_version_file(x) for x in value]
        return [parse_version_file(value)]
