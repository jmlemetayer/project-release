"""All the project errors."""

from pathlib import Path
from typing import List
from typing import Union


class ProjectReleaseError(Exception):
    """The project base exception."""

    @classmethod
    def _relpath(cls, path: Union[Path, str]) -> Path:
        if isinstance(path, str):
            path = Path(path)
        try:
            return path.relative_to(Path.cwd())
        except ValueError:
            return path


class InvalidUtf8FileError(ProjectReleaseError):
    """The specified file is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid UTF-8 file")


class InvalidYamlFileError(ProjectReleaseError):
    """The specified YAML file is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid YAML file")


class InvalidConfigFileError(ProjectReleaseError):
    """The specified configuration file is invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid configuration file")


class VersionNotFoundError(ProjectReleaseError):
    """No version has been found."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"No version found in file: {self._relpath(path)}")


class VersionEmptyError(ProjectReleaseError):
    """An empty version has been found."""

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"Empty version found in file: {self._relpath(path)}")


class VersionInconsistentError(ProjectReleaseError):
    """Multiple inconsistent versions has been found."""

    def __init__(self, path: Union[Path, str], versions: List[str]) -> None:
        super().__init__(
            "Multiple inconsistent versions found in file: "
            f"{self._relpath(path)}: {versions}"
        )
