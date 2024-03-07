"""The command line module."""
import argparse
import logging
from pathlib import Path
from typing import List
from typing import Optional

import colorlog

from . import __version__
from .config import CONFIG_FILE
from .config import CONFIG_HELP
from .config import sample_config
from .error import ProjectReleaseError
from .fsm import FiniteStateMachine
from .git import current_repo
from .utils import log_exception

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
        "-c",
        "--config",
        type=Path,
        help=f"specify an alternate configuration file (default: {CONFIG_FILE})",
    )

    parser.add_argument(
        "--sample-config", action="store_true", help=f"print a sample {CONFIG_FILE}"
    )

    parser.add_argument(
        "--no-color",
        action="store_false",
        dest="color",
        help="do not colorize the output",
    )

    fsm_group = parser.add_argument_group("state options")
    fsm_group.add_argument(
        "--status", action="store_true", help="show the release status"
    )
    fsm_group.add_argument(
        "--continue",
        action="store_true",
        dest="cnotinue",
        help="continue the release process",
    )
    fsm_group.add_argument(
        "--abort", action="store_true", help="abort the release process"
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
        fsm = FiniteStateMachine(repo)

        if args.status:
            fsm.status()
            return 0

        if args.abort:
            fsm.abort()
            return 0

        if fsm.is_configured():
            if not args.cnotinue:
                raise SystemExit("You are currently releasing a new version")

            fsm.cnotinue()
            return 0

        fsm.configure(args.config)
        fsm.run()

    except (ProjectReleaseError, SystemExit) as exc:
        log_exception(exc, level=logging.CRITICAL)
        return 1

    except (KeyboardInterrupt, EOFError):
        logger.info("Cancelled by user")

    return 0
