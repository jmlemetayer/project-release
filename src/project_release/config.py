"""Config related code."""
import logging
import pathlib
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Union

import yaml
from schema import And
from schema import Optional
from schema import Or
from schema import Schema
from schema import SchemaError
from schema import Use

from .convention import AcceptAllValidator
from .convention import Pep440Validator
from .convention import SemverValidator
from .file import EditedVersionFile
from .file import FormattedVersionFile
from .file import PlainVersionFile

logger = logging.getLogger(__name__)


def _schema_list_like(schema: Schema) -> Schema:
    return Schema(Or(And(schema, Use(lambda x: [x])), [schema]))


class Config:
    """A class to handle the config file."""

    __DEFAULT_CONVENTION_VERSION = None
    __DEFAULT_GIT_COMMIT_MESSAGE = "bump: version %(version)s"
    __DEFAULT_GIT_COMMIT_SIGN_OFF = False
    __DEFAULT_GIT_COMMIT_GPG_SIGN = False
    __DEFAULT_GIT_TAG_FORMAT = "%(version)s"
    __DEFAULT_GIT_TAG_MESSAGE = "version %(version)s"
    __DEFAULT_GIT_TAG_ANNOTATE = False
    __DEFAULT_GIT_TAG_GPG_SIGN = False

    __SCHEMA_CONVENTION_VERSION = Schema(
        And(str, Use(str.lower), lambda x: x in ("semver", "pep440"))
    )

    __SCHEMA_CONVENTION = Schema(
        {
            Optional(
                "version", default=__DEFAULT_CONVENTION_VERSION
            ): __SCHEMA_CONVENTION_VERSION
        }
    )

    __SCHEMA_FILE_VERSION_PLAIN = Schema(
        Or(
            And(str, len, Use(lambda x: {"path": x})),
            {"path": And(str, len)},
        )
    )

    __SCHEMA_FILE_VERSION_FORMATTED = Schema(
        {"path": And(str, len), "format": And(str, len)}
    )

    __SCHEMA_FILE_VERSION_EDITED = Schema(
        {"path": And(str, len), "pattern": And(str, len)}
    )

    __SCHEMA_FILE_VERSION = Schema(
        Or(
            __SCHEMA_FILE_VERSION_PLAIN,
            __SCHEMA_FILE_VERSION_FORMATTED,
            __SCHEMA_FILE_VERSION_EDITED,
        )
    )

    __SCHEMA_FILE_VERSION_LIST = _schema_list_like(__SCHEMA_FILE_VERSION)

    __SCHEMA_FILE = Schema(
        {
            Optional("version", default=[]): __SCHEMA_FILE_VERSION_LIST,
        }
    )

    __SCHEMA_GIT_BRANCH_ITEM = And(str, len)

    __SCHEMA_GIT_BRANCH_LIST = _schema_list_like(__SCHEMA_GIT_BRANCH_ITEM)

    __SCHEMA_GIT_BRANCH = Schema(
        {
            Optional("development", default=[]): __SCHEMA_GIT_BRANCH_LIST,
            Optional("release", default=[]): __SCHEMA_GIT_BRANCH_LIST,
        }
    )

    __SCHEMA_GIT_COMMIT = Schema(
        {
            Optional("message", default=__DEFAULT_GIT_COMMIT_MESSAGE): And(str, len),
            Optional("sign-off", default=__DEFAULT_GIT_COMMIT_SIGN_OFF): bool,
            Optional("gpg-sign", default=__DEFAULT_GIT_COMMIT_GPG_SIGN): bool,
        }
    )

    __SCHEMA_GIT_TAG = Schema(
        {
            Optional("format", default=__DEFAULT_GIT_TAG_FORMAT): And(str, len),
            Optional("message", default=__DEFAULT_GIT_TAG_MESSAGE): And(str, len),
            Optional("annotate", default=__DEFAULT_GIT_TAG_ANNOTATE): bool,
            Optional("gpg-sign", default=__DEFAULT_GIT_TAG_GPG_SIGN): bool,
        }
    )

    __SCHEMA_GIT = Schema(
        {
            Optional(
                "branch", default=__SCHEMA_GIT_BRANCH.validate({})
            ): __SCHEMA_GIT_BRANCH,
            Optional(
                "commit", default=__SCHEMA_GIT_COMMIT.validate({})
            ): __SCHEMA_GIT_COMMIT,
            Optional("tag", default=__SCHEMA_GIT_TAG.validate({})): __SCHEMA_GIT_TAG,
        }
    )

    __SCHEMA = Schema(
        {
            Optional(
                "convention", default=__SCHEMA_CONVENTION.validate({})
            ): __SCHEMA_CONVENTION,
            Optional("file", default=__SCHEMA_FILE.validate({})): __SCHEMA_FILE,
            Optional("git", default=__SCHEMA_GIT.validate({})): __SCHEMA_GIT,
        }
    )

    def __init__(self, path: Union[Path, str]) -> None:
        self.__path = path
        self.__config: Dict[str, Any] = {
            "version_files": [],
            "development_branches": [],
            "release_branches": [],
        }

    def __parse_convention(self, data: Dict[str, Any]) -> None:
        """Parse the 'convention' dictionary."""
        version = data["version"]
        if version == self.__DEFAULT_CONVENTION_VERSION:
            self.__config["version_validator"] = AcceptAllValidator()
        elif version == "semver":
            self.__config["version_validator"] = SemverValidator()
        elif version == "pep440":
            self.__config["version_validator"] = Pep440Validator()

    def __parse_version_file(self, data: Dict[str, Any]) -> None:
        """Parse the 'file.version' item."""
        path = data["path"]
        f0rmat = data.get("format")
        pattern = data.get("pattern")

        if f0rmat is not None:
            self.__config["version_files"].append(FormattedVersionFile(path, f0rmat))
        elif pattern is not None:
            self.__config["version_files"].append(EditedVersionFile(path, pattern))
        else:
            self.__config["version_files"].append(PlainVersionFile(path))

    def __parse_file(self, data: Dict[str, Any]) -> None:
        """Parse the 'file' dictionary."""
        for version_file in data["version"]:
            self.__parse_version_file(version_file)

    def __parse_branch(self, data: Dict[str, Any]) -> None:
        """Parse the 'git.branch' dictionary."""
        for branch in data["development"]:
            self.__config["development_branches"].append(branch)
        for branch in data["release"]:
            self.__config["release_branches"].append(branch)

    def __parse_commit(self, data: Dict[str, Any]) -> None:
        """Parse the 'git.commit' dictionary."""
        self.__config["commit_message"] = data["message"]
        self.__config["commit_sign_off"] = data["sign-off"]
        self.__config["commit_gpg_sign"] = data["gpg-sign"]

    def __parse_tag(self, data: Dict[str, Any]) -> None:
        """Parse the 'git.tag' dictionary."""
        self.__config["tag_format"] = data["format"]
        self.__config["tag_message"] = data["message"]
        self.__config["tag_annotate"] = data["annotate"]
        self.__config["tag_gpg_sign"] = data["gpg-sign"]

    def __parse_git(self, data: Dict[str, Any]) -> None:
        """Parse the 'git' dictionary."""
        self.__parse_branch(data["branch"])
        self.__parse_commit(data["commit"])
        self.__parse_tag(data["tag"])

    def parse(self) -> None:
        """Parse the config file.

        Raises
        ------
        yaml.YAMLError
            If the yaml syntax is invalid.
        SchemaError
            If the data schema is invalid.
        """
        with open(self.__path, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        validated = self.__SCHEMA.validate(data)

        self.__parse_convention(validated["convention"])
        self.__parse_file(validated["file"])
        self.__parse_git(validated["git"])

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


def parse_config(config_file: pathlib.Path) -> Config:
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
    if not config_file.exists():
        raise SystemExit("Configuration file not found")
    if not config_file.is_file():
        raise SystemExit("The configuration file is not a regular file")

    config = Config(config_file)

    try:
        config.parse()
    except yaml.YAMLError as exc:
        desc = ""
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            desc = f": syntax error at line {mark.line + 1}, column {mark.column + 1}"
        raise SystemExit(
            f"The configuration file is not a valid yaml file{desc}"
        ) from exc
    except SchemaError as exc:
        raise SystemExit(f"The configuration file is not valid: {exc}") from exc

    return config
