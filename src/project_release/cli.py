"""The command line module."""
import argparse
import logging
import pathlib
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

import git
import questionary
import schema
import yaml

from . import __version__
from .config import Config
from .git import current_git_repo

logger = logging.getLogger(__name__)

CONFIG_FILE = ".project-release-config.yaml"


def _get_remote(git_repo: git.Repo, git_remote: Optional[str]) -> Optional[str]:
    git_remotes = [x.name for x in git_repo.remotes]
    if git_remote is not None:
        if git_remote not in git_remotes:
            raise SystemExit(f"Invalid git remote: '{git_remote}'")
        return git_remote
    if not git_remotes:
        return None
    if len(git_remotes) == 1:
        return git_remotes[0]
    return questionary.select(
        "Select the git remote to use", choices=[x.name for x in git_repo.remotes]
    ).unsafe_ask()


def _get_version(
    version: Optional[str], validate: Callable[[str], Union[bool, str]]
) -> str:
    if version is not None:
        if validate(version) is not True:
            raise SystemExit(validate(version))
        return version
    return questionary.text(
        "Specify the desired version string", validate=validate
    ).unsafe_ask()


def project_release_cli(argv: Optional[List[str]] = None) -> int:
    """Entry point for the command line.

    Parameters
    ----------
    argv: list of str, optional
        List of command line arguments.

    Returns
    -------
    int
        The value to be returned by the CLI executable.
    """
    parser = argparse.ArgumentParser(
        prog="project-release", description="A tool to help releasing projects."
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logs")

    parser.add_argument("VERSION", nargs="?", help="desired version string")

    parser.add_argument(
        "-c",
        "--config",
        default=CONFIG_FILE,
        help="specify an alternate configuration file",
    )

    git_group = parser.add_argument_group("git options")

    git_group.add_argument("--git-remote", help="specify the git remote to use")

    args = parser.parse_args(args=argv)

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    git_repo = current_git_repo()

    git_dir = pathlib.Path(git_repo.git_dir)

    config_file = git_dir.parent / args.config

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

    try:
        version = _get_version(args.VERSION, config["version_validator"].validate)

        git_remote = _get_remote(git_repo, args.git_remote)
    except KeyboardInterrupt as exc:
        raise SystemExit("Cancelled by user") from exc

    logger.info("Selected version string: %s", version)
    logger.info("Selected git remote: %s", git_remote)

    return 0
