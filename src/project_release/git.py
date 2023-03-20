"""Git related code."""
import logging

import git

logger = logging.getLogger(__name__)


def current_git_repo() -> git.Repo:
    """Return the current git repository.

    Returns
    -------
    git.Repo
        The current git repository.

    Raises
    ------
    SystemExit
        If the git repository is invalid or dirty.
    """
    try:
        git_repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError as exc:
        raise SystemExit("Not in a git repository") from exc

    if git_repo.is_dirty():
        raise SystemExit("The git repository is dirty")

    return git_repo
