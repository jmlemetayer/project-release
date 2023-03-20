"""Config related code."""
import logging
import pathlib
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
            "git_development_branches": [],
            "git_development_branch": None,
            "git_release_branches": [],
            "git_release_branch": None,
            "git_commit_message": "bump: version %(version)s",
            "git_commit_sign_off": False,
            "git_commit_gpg_sign": False,
            "git_tag_format": "%(version)s",
            "git_tag_message": "version %(version)s",
            "git_tag_annotate": True,
            "git_tag_gpg_sign": False,
        }

    def __parse_list(
        self, data: Any, parse: Callable[..., None], **kwargs: Any
    ) -> None:
        """Parse an item which can be a list or a scalar."""
        if data is not None:
            if isinstance(data, list):
                for data_item in data:
                    parse(data_item, **kwargs)
            else:
                parse(data, **kwargs)

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

    def __parse_git_branch_item(self, data: Any, branch_name: str) -> None:
        """Parse the 'git.branch.<branch_name>' item."""
        self.__config[f"git_{branch_name}_branches"].append(data)

    def __parse_git_branch(self, data: Any) -> None:
        """Parse the 'git.branch' dictionary."""
        if data is not None:
            self.__parse_list(
                data.get("development"),
                self.__parse_git_branch_item,
                branch_name="development",
            )
            self.__parse_list(
                data.get("release"), self.__parse_git_branch_item, branch_name="release"
            )

    def __parse_git_commit(self, data: Any) -> None:
        """Parse the 'git.commit' dictionary."""
        if data is not None:
            message = data.get("message")
            if message is not None:
                self.__config["git_commit_message"] = message
            sign_off = data.get("sign-off")
            if sign_off is not None:
                self.__config["git_commit_sign_off"] = sign_off
            gpg_sign = data.get("gpg-sign")
            if gpg_sign is not None:
                self.__config["git_commit_gpg_sign"] = gpg_sign

    def __parse_git_tag(self, data: Any) -> None:
        """Parse the 'git.tag' dictionary."""
        if data is not None:
            f0rmat = data.get("format")
            if f0rmat is not None:
                self.__config["git_tag_format"] = f0rmat
            message = data.get("message")
            if message is not None:
                self.__config["git_tag_message"] = message
            annotate = data.get("annotate")
            if annotate is not None:
                self.__config["git_tag_annotate"] = annotate
            gpg_sign = data.get("gpg-sign")
            if gpg_sign is not None:
                self.__config["git_tag_gpg_sign"] = gpg_sign

    def __parse_git(self, data: Any) -> None:
        """Parse the 'git' dictionary."""
        if data is not None:
            self.__parse_git_branch(data.get("branch"))
            self.__parse_git_commit(data.get("commit"))
            self.__parse_git_tag(data.get("tag"))

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
        self.__parse_git(validated.get("git"))

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
    except schema.SchemaError as exc:
        raise SystemExit(f"The configuration file is not valid: {exc}") from exc

    return config
