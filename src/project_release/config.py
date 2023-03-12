"""Config related code."""
import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Union

import schema
import yaml

from .file import EditedVersionFile
from .file import FormattedVersionFile
from .file import PlainVersionFile
from .validation import AcceptAllValidator
from .validation import Pep440Validator
from .validation import SemverValidator

logger = logging.getLogger(__name__)


class Config:
    """A class to handle the config file."""

    __VALIDATION_VERSION_SCHEMA = schema.Schema(
        schema.And(str, schema.Use(str.lower), lambda s: s in ("semver", "pep440"))
    )

    __VALIDATION_SCHEMA = schema.Schema(
        {schema.Optional("version"): __VALIDATION_VERSION_SCHEMA}
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

    __SCHEMA = schema.Schema(
        {
            schema.Optional("validation"): __VALIDATION_SCHEMA,
            schema.Optional("file"): __FILE_SCHEMA,
        }
    )

    def __init__(self, path: Union[Path, str]) -> None:
        self.__path = path
        self.__config: Dict[str, Any] = {
            "version_validator": AcceptAllValidator(),
            "version_files": [],
        }

    def __parse_validation(self, data: Any) -> None:
        """Parse the 'validation' dictionary."""
        validation = data.get("validation")
        if validation is not None:
            version = validation.get("version")
            if version == "semver":
                self.__config["version_validator"] = SemverValidator()
            elif version == "pep440":
                self.__config["version_validator"] = Pep440Validator()

    def __parse_version_files_item(self, data: Any) -> None:
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
        file = data.get("file")
        if file is not None:
            versions = file.get("version")
            if versions is not None:
                if isinstance(versions, list):
                    for version in versions:
                        self.__parse_version_files_item(version)
                else:
                    self.__parse_version_files_item(versions)

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

        self.__parse_validation(validated)
        self.__parse_file(validated)

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
