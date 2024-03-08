"""All the project errors."""

from pathlib import Path
from typing import List
from typing import Union

from .utils import relative_path


class ProjectReleaseError(Exception):
    """The project base exception."""


class InvalidUtf8FileError(ProjectReleaseError):
    """The specified file is invalid."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"Invalid UTF-8 file: {relative_path(path)}")


class InvalidYamlFileError(ProjectReleaseError):
    """The specified YAML file is invalid."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"Invalid YAML file: {relative_path(path)}")


class InvalidConfigFileError(ProjectReleaseError):
    """The specified configuration file is invalid."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"Invalid configuration file: {relative_path(path)}")


class VersionNotFoundError(ProjectReleaseError):
    """No version has been found."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"No version found in file: {relative_path(path)}")


class VersionEmptyError(ProjectReleaseError):
    """An empty version has been found."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"Empty version found in file: {relative_path(path)}")


class VersionInconsistentError(ProjectReleaseError):
    """Multiple inconsistent versions has been found."""

    def __init__(self, path: Union[Path, str], versions: List[str]) -> None:
        super().__init__(
            "Multiple inconsistent versions found in file: "
            f"{relative_path(path)}: {versions}"
        )
