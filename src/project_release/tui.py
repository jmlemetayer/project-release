"""Text-based user interface (TUI) related code."""
import logging
from typing import Callable
from typing import Optional
from typing import Union

import git
import questionary

logger = logging.getLogger(__name__)


def select_remote(repo: git.Repo, user_remote: Optional[str]) -> Optional[str]:
    """Select the git remote to use.

    Parameters
    ----------
    repo
        The current git repository.
    user_remote
        The user-specified git remote.

    Returns
    -------
    str or None
        The selected git remote or None if not available.

    Raises
    ------
    SystemExit
        If the specified git remote is invalid.
    """
    available_remotes = [x.name for x in repo.remotes]
    if user_remote is not None:
        if user_remote not in available_remotes:
            raise SystemExit(f"Invalid git remote: '{user_remote}'")
        return user_remote
    if not available_remotes:
        return None
    if len(available_remotes) == 1:
        return available_remotes[0]
    return questionary.select(
        "Select the git remote to use", choices=[x.name for x in repo.remotes]
    ).unsafe_ask()


def select_version(
    user_version: Optional[str], validate: Callable[[str], Union[bool, str]]
) -> str:
    """Select the version to use.

    Parameters
    ----------
    user_version
        The user-specified version.
    validate
        A function used to validate the version.

    Returns
    -------
    str
        The selected version.

    Raises
    ------
    SystemExit
        If the specified version is invalid.
    """
    if user_version is not None:
        if validate(user_version) is not True:
            raise SystemExit(validate(user_version))
        return user_version
    return questionary.text(
        "Specify the desired version string", validate=validate
    ).unsafe_ask()
