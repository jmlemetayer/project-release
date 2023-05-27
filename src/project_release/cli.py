"""The command line module."""
import argparse
import logging
import pathlib
from typing import List
from typing import Optional

from . import __version__
from .config import parse_config
from .git import current_branch_name
from .git import current_repo
from .git import repo_branch_names
from .tui import select_branch_name
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

    git_group.add_argument("--remote", help="specify the remote to use")
    git_group.add_argument(
        "--development-branch", help="specify the development branch to use"
    )
    git_group.add_argument("--release-branch", help="specify the release branch to use")

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

        # Select the remote
        remote = select_remote(repo, args.remote)
        logger.info("Selected remote: %s", remote)

        # Select the development branch name
        development_branch_name = select_branch_name(
            branch_description="development",
            config_branches=config["development_branches"],
            repo_branches=repo_branch_names(repo, remote),
            user_branch=args.development_branch,
            default_branch=current_branch_name(repo),
        )
        logger.info("Selected development branch: %s", development_branch_name)

        # Select the release branch name
        release_branch_name = select_branch_name(
            branch_description="release",
            config_branches=config["release_branches"],
            repo_branches=repo_branch_names(repo, remote),
            user_branch=args.release_branch,
            default_branch=development_branch_name,
        )
        logger.info("Selected release branch: %s", release_branch_name)

        # Select the version
        version = select_version(args.VERSION, config["version_validator"].validate)
        logger.info("Selected version string: %s", version)

    except (KeyboardInterrupt, EOFError) as exc:
        raise SystemExit("Cancelled by user") from exc

    return 0
