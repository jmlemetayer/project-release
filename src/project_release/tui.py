"""Text-based user interface (TUI) related code."""
import logging
from typing import Callable
from typing import Optional
from typing import Union

import git
import questionary

logger = logging.getLogger(__name__)


def select_git_remote(git_repo: git.Repo, git_remote: Optional[str]) -> Optional[str]:
    """Select the git remote to use.

    Parameters
    ----------
    git_repo
        The current git repository.
    git_remote
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
    available_git_remotes = [x.name for x in git_repo.remotes]
    if git_remote is not None:
        if git_remote not in available_git_remotes:
            raise SystemExit(f"Invalid git remote: '{git_remote}'")
        return git_remote
    if not available_git_remotes:
        return None
    if len(available_git_remotes) == 1:
        return available_git_remotes[0]
    return questionary.select(
        "Select the git remote to use", choices=[x.name for x in git_repo.remotes]
    ).unsafe_ask()


def select_version(
    version: Optional[str], validate: Callable[[str], Union[bool, str]]
) -> str:
    """Select the version to use.

    Parameters
    ----------
    git_repo
        The current git repository.
    git_remote
        The user-specified git remote.

    Returns
    -------
    str
        The selected version.

    Raises
    ------
    SystemExit
        If the specified version is invalid.
    """
    if version is not None:
        if validate(version) is not True:
            raise SystemExit(validate(version))
        return version
    return questionary.text(
        "Specify the desired version string", validate=validate
    ).unsafe_ask()
