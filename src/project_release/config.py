"""Config related code."""
import logging
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Union

import schema
import yaml

from .convention import AcceptAllValidator
from .convention import Pep440Validator
from .convention import SemverValidator
from .file import EditedVersionFile
from .file import FormattedVersionFile
from .file import PlainVersionFile

logger = logging.getLogger(__name__)


class Config:
    """A class to handle the config file."""

    __CONVENTION_VERSION_SCHEMA = schema.Schema(
        schema.And(str, schema.Use(str.lower), lambda s: s in ("semver", "pep440"))
    )

    __CONVENTION_SCHEMA = schema.Schema(
        {schema.Optional("version"): __CONVENTION_VERSION_SCHEMA}
    )

    __FILE_VERSION_PLAIN_SCHEMA = schema.Schema(
        schema.Or({"path": schema.And(str, len)}, schema.And(str, len))
    )

    __FILE_VERSION_FORMATTED_SCHEMA = schema.Schema(
        {"path": schema.And(str, len), "format": schema.And(str, len)}
    )

    __FILE_VERSION_EDITED_SCHEMA = schema.Schema(
        {"path": schema.And(str, len), "pattern": schema.And(str, len)}
    )

    __FILE_VERSION_SCALAR_SCHEMA = schema.Schema(
        schema.Or(
            __FILE_VERSION_PLAIN_SCHEMA,
            __FILE_VERSION_FORMATTED_SCHEMA,
            __FILE_VERSION_EDITED_SCHEMA,
        )
    )

    __FILE_VERSION_SCHEMA = schema.Schema(
        schema.Or([__FILE_VERSION_SCALAR_SCHEMA], __FILE_VERSION_SCALAR_SCHEMA)
    )

    __FILE_SCHEMA = schema.Schema(
        {
            schema.Optional("version"): __FILE_VERSION_SCHEMA,
        }
    )

    __GIT_BRANCH_ITEM_SCALAR_SCHEMA = schema.And(str, len)

    __GIT_BRANCH_ITEM_SCHEMA = schema.Schema(
        schema.Or([__GIT_BRANCH_ITEM_SCALAR_SCHEMA], __GIT_BRANCH_ITEM_SCALAR_SCHEMA)
    )

    __GIT_BRANCH_SCHEMA = schema.Schema(
        {
            schema.Optional("development"): __GIT_BRANCH_ITEM_SCHEMA,
            schema.Optional("release"): __GIT_BRANCH_ITEM_SCHEMA,
        }
    )

    __GIT_COMMIT_SCHEMA = schema.Schema(
        {
            schema.Optional("message"): schema.And(str, len),
            schema.Optional("sign-off"): bool,
            schema.Optional("gpg-sign"): bool,
        }
    )

    __GIT_TAG_SCHEMA = schema.Schema(
        {
            schema.Optional("format"): schema.And(str, len),
            schema.Optional("message"): schema.And(str, len),
            schema.Optional("annotate"): bool,
            schema.Optional("gpg-sign"): bool,
        }
    )

    __GIT_SCHEMA = schema.Schema(
        {
            schema.Optional("branch"): __GIT_BRANCH_SCHEMA,
            schema.Optional("commit"): __GIT_COMMIT_SCHEMA,
            schema.Optional("tag"): __GIT_TAG_SCHEMA,
        }
    )

    __SCHEMA = schema.Schema(
        {
            schema.Optional("convention"): __CONVENTION_SCHEMA,
            schema.Optional("file"): __FILE_SCHEMA,
            schema.Optional("git"): __GIT_SCHEMA,
        }
    )

    def __init__(self, path: Union[Path, str]) -> None:
        self.__path = path
        self.__config: Dict[str, Any] = {
            "version_validator": AcceptAllValidator(),
            "version_files": [],
        }

    def __parse_list(self, data: Any, parse: Callable[[Any], None]) -> None:
        """Parse an item which can be a list or a scalar."""
        if data is not None:
            if isinstance(data, list):
                for data_item in data:
                    parse(data_item)
            else:
                parse(data)

    def __parse_convention(self, data: Any) -> None:
        """Parse the 'convention' dictionary."""
        if data is not None:
            version = data.get("version")
            if version == "semver":
                self.__config["version_validator"] = SemverValidator()
            elif version == "pep440":
                self.__config["version_validator"] = Pep440Validator()

    def __parse_version_file(self, data: Any) -> None:
        """Parse the 'file.version' item."""
        if isinstance(data, str):
            return self.__config["version_files"].append(PlainVersionFile(data))

        path = data.get("path")
        f0rmat = data.get("format")
        pattern = data.get("pattern")

        if f0rmat is not None:
            return self.__config["version_files"].append(
                FormattedVersionFile(path, f0rmat)
            )
        if pattern is not None:
            return self.__config["version_files"].append(
                EditedVersionFile(path, pattern)
            )
        return self.__config["version_files"].append(PlainVersionFile(path))

    def __parse_file(self, data: Any) -> None:
        """Parse the 'file' dictionary."""
        if data is not None:
            self.__parse_list(data.get("version"), self.__parse_version_file)

    def parse(self) -> None:
        """Parse the config file.

        Raises
        ------
        yaml.YAMLError
            If the yaml syntax is invalid.
        schema.SchemaError
            If the data schema is invalid.
        """
        with open(self.__path, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        validated = self.__SCHEMA.validate(data)

        self.__parse_convention(validated.get("convention"))
        self.__parse_file(validated.get("file"))

    def __getitem__(self, key: str) -> Any:
        """Get a value from the configuration.

        See Also
        --------
        object.__getitem__
        """
        return self.__config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value to the configuration.

        See Also
        --------
        object.__setitem__
        """
        self.__config[key] = value
