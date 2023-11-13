"""The command line module."""
import argparse
import logging
import pathlib
from typing import List
from typing import Optional

from . import __version__
from .config import parse_config
from .error import ProjectReleaseError
from .git import create_branch
from .git import current_branch_name
from .git import current_repo
from .git import local_branch_names
from .git import repo_branch_names
from .git import update_branch
from .tui import select_branch_name
from .tui import select_remote
from .tui import select_version

logger = logging.getLogger(__name__)

CONFIG_FILE = ".project-release-config.yaml"


def project_release_cli(argv: Optional[List[str]] = None) -> int:  # noqa: PLR0915
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

    git_group.add_argument(
        "--no-fetch",
        dest="fetch",
        action="store_false",
        help="do no fetch refs from the remote",
    )
    git_group.add_argument(
        "--no-update",
        dest="update",
        action="store_false",
        help="do no update the local branches from the remote",
    )
    git_group.add_argument(
        "-f",
        "--force-update",
        action="store_true",
        help="""
        update local branches from the remote,
        regardless of whether they have diverged
        """,
    )

    args = parser.parse_args(args=argv)

    if not args.update:
        args.fetch = False

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
            config_branches=config.git.branch.development,
            repo_branches=repo_branch_names(repo, remote),
            user_branch=args.development_branch,
            default_branch=current_branch_name(repo),
        )
        logger.info("Selected development branch: %s", development_branch_name)

        # Select the release branch name
        release_branch_name = select_branch_name(
            branch_description="release",
            config_branches=config.git.branch.release,
            repo_branches=repo_branch_names(repo, remote),
            user_branch=args.release_branch,
            default_branch=development_branch_name,
        )
        logger.info("Selected release branch: %s", release_branch_name)

        # Fetch the remote
        if remote and args.fetch:
            logger.debug("Fetching refs from remote %s", remote)
            remote.fetch()

        # Update the development and release branches
        if development_branch_name not in local_branch_names(repo):
            raise SystemExit(
                f"The {development_branch_name} branch does not exists locally"
            )
        development_branch = repo.heads[development_branch_name]

        if remote and args.update:
            update_branch(development_branch, remote, args.force_update)

        if release_branch_name not in local_branch_names(repo):
            release_branch = create_branch(
                release_branch_name, development_branch, remote
            )
        else:
            release_branch = repo.heads[release_branch_name]

            if remote and args.update:
                update_branch(release_branch, remote, args.force_update)

        # Checkout the release branch
        logger.debug("Switching to the %s branch", release_branch)
        release_branch.checkout()

        # Select the version
        version = select_version(
            args.VERSION, config.convention.version.validate_version
        )
        logger.info("Selected version string: %s", version)

    except ProjectReleaseError as exc:
        raise SystemExit(str(exc)) from exc

    except (KeyboardInterrupt, EOFError) as exc:
        raise SystemExit("Cancelled by user") from exc

    return 0
