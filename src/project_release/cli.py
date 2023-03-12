"""The command line module."""
import argparse
import logging
import pathlib
import sys
from typing import List
from typing import Optional

import git
import questionary

from . import __version__

logger = logging.getLogger(__name__)

CONFIG_FILE = ".project-release-config.yaml"


def _get_version(version: Optional[str]) -> str:
    if version is None:
        return questionary.text("Specify the desired version string").unsafe_ask()
    return version


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

    args = parser.parse_args(args=argv)

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    try:
        git_repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        sys.exit("Not in a git repository")

    if git_repo.is_dirty():
        sys.exit("The git repository is dirty")

    git_dir = pathlib.Path(git_repo.git_dir)

    config_file = git_dir.parent / args.config

    if not config_file.exists():
        sys.exit("Configuration file not found")

    if not config_file.is_file():
        sys.exit("The configuration file is not a regular file")

    try:
        version = _get_version(args.VERSION)
    except KeyboardInterrupt:
        sys.exit("Cancelled by user")

    logger.info("Selected version string: %s", version)

    return 0
