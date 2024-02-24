"""The command line module."""
import argparse
import logging
from typing import List
from typing import Optional

from . import __version__
from .config import CONFIG_FILE
from .config import CONFIG_HELP
from .config import sample_config
from .error import ProjectReleaseError

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
        "--sample-config", action="store_true", help=f"print a sample {CONFIG_FILE}"
    )

    args = parser.parse_args(args=argv)

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    try:
        if args.sample_config:
            sample_config()
            return 0

    except ProjectReleaseError as exc:
        raise SystemExit(str(exc)) from exc

    except (KeyboardInterrupt, EOFError) as exc:
        raise SystemExit("Cancelled by user") from exc

    return 0
