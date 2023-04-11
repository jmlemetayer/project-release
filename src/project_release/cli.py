"""The command line module."""
import argparse
import logging
import pathlib
from typing import List
from typing import Optional

from . import __version__
from .config import parse_config
from .git import current_branch
from .git import current_branches
from .git import current_repo
from .tui import select_branch
from .tui import select_remote
from .tui import select_version

logger = logging.getLogger(__name__)

CONFIG_FILE = ".project-release-config.yaml"


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

    git_group.add_argument("--remote", help="specify the git remote to use")
    git_group.add_argument(
        "--development-branch", help="specify the git development branch to use"
    )
    git_group.add_argument(
        "--release-branch", help="specify the git release branch to use"
    )

    args = parser.parse_args(args=argv)

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    try:
        repo = current_repo()
        git_dir = pathlib.Path(repo.git_dir)
        config_file = git_dir.parent / args.config
        config = parse_config(config_file)

        # Select the git remote
        remote = select_remote(repo, args.remote)
        logger.info("Selected git remote: %s", remote)

        branches = current_branches(repo, remote)
        default_branch = current_branch(repo)

        # Select the git development branch
        development_branch = select_branch(
            "development",
            config["development_branches"],
            branches,
            args.development_branch,
            default_branch,
        )
        logger.info("Selected git development branch: %s", development_branch)

        # Select the git release branch
        release_branch = select_branch(
            "release",
            config["release_branches"],
            branches,
            args.release_branch,
            development_branch,
        )
        logger.info("Selected git release branch: %s", release_branch)

        # Select the version
        version = select_version(args.VERSION, config["version_validator"].validate)
        logger.info("Selected version string: %s", version)

    except (KeyboardInterrupt, EOFError) as exc:
        raise SystemExit("Cancelled by user") from exc

    return 0
