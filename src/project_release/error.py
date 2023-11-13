"""All the project errors."""

from pathlib import Path
from typing import List
from typing import Union

from pydantic import ValidationError
from yaml import MarkedYAMLError
from yaml import YAMLError


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

    def __init__(self, exc: Exception) -> None:
        super().__init__(f"Invalid UTF-8 file: {exc}")


class InvalidYamlFileError(ProjectReleaseError):
    """The specified YAML file is invalid."""

    def __init__(self, exc: YAMLError) -> None:
        lines: List[str] = []
        if isinstance(exc, MarkedYAMLError):
            if exc.problem_mark:
                mark = exc.problem_mark
                lines.append(f"at line {mark.line + 1}, column {mark.column + 1}")
            if exc.context:
                lines.append(str(exc.context))
            if exc.problem:
                lines.append(str(exc.problem))
        desc = "syntax error " + ", ".join(lines) if lines else str(exc)
        super().__init__(f"Invalid YAML file: {desc}")


class InvalidConfigFileError(ProjectReleaseError):
    """The specified configuration file is invalid."""

    def __init__(self, exc: ValidationError) -> None:
        super().__init__(f"Invalid configuration file: {exc}")


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
