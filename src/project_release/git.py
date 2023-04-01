"""Git related code."""
import logging
from typing import List
from typing import Optional

import git

logger = logging.getLogger(__name__)


def current_repo() -> git.Repo:
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
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError as exc:
        raise SystemExit("Not in a git repository") from exc

    if repo.is_dirty():
        raise SystemExit("The git repository is dirty")

    return repo


def get_local_branches(repo: git.Repo) -> List[str]:
    """Return the local branches.

    Parameters
    ----------
    repo
        The current git repository.

    Returns
    -------
    list of str
        The local branches.
    """
    return [branch.name for branch in repo.heads]


def get_remote_branches(repo: git.Repo, remote: Optional[str]) -> List[str]:
    """Return the remote branches.

    Parameters
    ----------
    repo
        The current git repository.
    remote
        The selected git remote.

    Returns
    -------
    list of str
        The remote branches.
    """
    if remote is None:
        return []
    return [
        ref.name.replace(f"{remote}/", "")
        for ref in repo.remote(remote).refs
        if not ref.name.endswith("HEAD")
    ]


def get_all_branches(repo: git.Repo, remote: Optional[str]) -> List[str]:
    """Return the local and remote branches.

    Parameters
    ----------
    repo
        The current git repository.
    remote
        The selected git remote.

    Returns
    -------
    list of str
        The local and remote branches.
    """
    local_branches = get_local_branches(repo)
    remote_branches = get_remote_branches(repo, remote)
    return list({*local_branches, *remote_branches})
