"""Text-based user interface (TUI) related code."""

import fnmatch
import logging
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

import git
import questionary

logger = logging.getLogger(__name__)


def select_remote(repo: git.Repo, remote_name: Optional[str]) -> Optional[git.Remote]:
    """Select the remote to use.

    Parameters
    ----------
    repo
        The current git repository.
    remote_name
        The user-specified remote name.

    Returns
    -------
    git.Remote or None
        The selected remote or None if not available.

    Raises
    ------
    SystemExit
        If the specified remote is invalid.
    """
    available_remote_names = [x.name for x in repo.remotes]
    if remote_name is not None:
        if remote_name not in available_remote_names:
            raise SystemExit(f"Invalid remote: '{remote_name}'")
        return repo.remote(remote_name)
    if not available_remote_names:
        return None
    if len(available_remote_names) == 1:
        return repo.remote(available_remote_names[0])
    selected_remote = questionary.select(
        "Select the remote to use", choices=available_remote_names
    ).unsafe_ask()
    return repo.remote(selected_remote)


def select_branch_name(
    branch_description: str,
    config_branches: List[str],
    repo_branches: List[str],
    user_branch: Optional[str],
    default_branch: Optional[str],
) -> str:
    """Select the branch name to use.

    Parameters
    ----------
    branch_description
        The description of the branch.
    config_branches
        The branch names available in configuration.
    repo_branches
        The branch names available in the repository.
    user_branch
        The user-specified branch name.
    default_branch
        The default branch name.

    Returns
    -------
    str
        The selected branch name.

    Raises
    ------
    SystemExit
        If the specified branch is invalid.
    """

    def is_pattern_branch(branch_name: str) -> bool:
        return any(c in branch_name for c in ["*", "?", "["])

    plain_branches = [b for b in config_branches if not is_pattern_branch(b)]
    pattern_branches = [b for b in config_branches if b not in plain_branches]

    def validate_branch(branch_name: str) -> Union[bool, str]:
        if branch_name in plain_branches:
            return True
        for pattern in pattern_branches:
            if fnmatch.fnmatchcase(branch_name, pattern):
                return True
        return f"Invalid branch name: '{branch_name}'"

    if user_branch is not None:
        if validate_branch(user_branch) is not True:
            raise SystemExit(validate_branch(user_branch))
        return user_branch
    if not pattern_branches and len(plain_branches) == 1:
        return plain_branches[0]

    potential_branches = [b for b in repo_branches if validate_branch(b) is True]
    potential_branches = list({*potential_branches, *plain_branches})

    if potential_branches:
        return questionary.autocomplete(
            f"Specify the desired {branch_description} branch",
            default=default_branch or "",
            choices=potential_branches,
            validate=validate_branch,
        ).unsafe_ask()
    return questionary.text(
        f"Specify the desired {branch_description} branch",
        default=default_branch or "",
        validate=validate_branch,
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
