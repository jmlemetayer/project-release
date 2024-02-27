"""The command line module."""
import argparse
import logging
import pathlib
from typing import List
from typing import Optional

import colorlog

from . import __version__
from .config import CONFIG_FILE
from .config import CONFIG_HELP
from .config import parse_config
from .config import sample_config
from .error import ProjectReleaseError
from .git import current_repo

logger = logging.getLogger(__name__)


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
        prog="project-release",
        description="A tool to help releasing projects.",
        epilog=f"{CONFIG_HELP}.",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logs")

    parser.add_argument(
        "--no-color",
        action="store_false",
        dest="color",
        help="do not colorize the output",
    )

    parser.add_argument(
        "-c",
        "--config",
        default=CONFIG_FILE,
        help="specify an alternate configuration file",
    )

    parser.add_argument(
        "--sample-config", action="store_true", help=f"print a sample {CONFIG_FILE}"
    )

    args = parser.parse_args(args=argv)

    logging_format = "%(levelname)-8s %(message)s"
    logging_level = logging.DEBUG if args.verbose else logging.INFO

    if args.color:
        logging_handler = colorlog.StreamHandler()
        logging_handler.setFormatter(
            colorlog.ColoredFormatter(f"%(log_color)s{logging_format}")
        )
        logging.basicConfig(handlers=[logging_handler], level=logging_level)
    else:
        logging.basicConfig(format=logging_format, level=logging_level)

    try:
        if args.sample_config:
            sample_config()
            return 0

        repo = current_repo()

        git_dir = pathlib.Path(repo.git_dir)
        config_file = git_dir.parent / args.config
        config = parse_config(config_file)  # noqa: F841

    except ProjectReleaseError as exc:
        raise SystemExit(str(exc)) from exc

    except (KeyboardInterrupt, EOFError) as exc:
        raise SystemExit("Cancelled by user") from exc

    return 0
