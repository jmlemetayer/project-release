"""Git related code."""
import enum
import logging
from typing import List
from typing import Optional

import git
from pydantic import Field
from pydantic import field_validator
from pydantic import validate_call

from ._pydantic import Listable
from ._pydantic import UseDefaultValueModel

logger = logging.getLogger(__name__)


class GitBanchConfig(UseDefaultValueModel):
    """Git branch configuration."""

    development: List[str] = []  # noqa: RUF012
    release: List[str] = []  # noqa: RUF012

    @field_validator("development", "release", mode="before")
    @classmethod
    @validate_call
    def _validate_branches(cls, value: Optional[Listable[str]]) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]


class GitCommitConfig(UseDefaultValueModel):
    """Git commit configuration."""

    message: str = "bump: version %(version)s"
    sign_off: bool = Field(default=False, alias="sign-off")
    gpg_sign: bool = Field(default=False, alias="gpg-sign")


class GitTagConfig(UseDefaultValueModel):
    """Git tag configuration."""

    fromat: str = Field(default="%(version)s", alias="format")
    message: str = "version %(version)s"
    annotate: bool = True
    gpg_sign: bool = Field(default=False, alias="gpg-sign")


class GitConfig(UseDefaultValueModel):
    """Git configuration."""

    branch: GitBanchConfig = GitBanchConfig()
    commit: GitCommitConfig = GitCommitConfig()
    tag: GitTagConfig = GitTagConfig()


def current_repo() -> git.Repo:
    """Return the current git repository.

    Returns
    -------
    git.repo.base.Repo
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

    # if repo.is_dirty():
    #    raise SystemExit("The git repository is dirty")

    return repo


def local_branch_names(repo: git.Repo) -> List[str]:
    """Return the local branches.

    Parameters
    ----------
    repo
        The current git repository.

    Returns
    -------
    list of str
        The local branch names.
    """
    return [branch.name for branch in repo.heads]


def remote_branch_names(remote: Optional[git.Remote]) -> List[str]:
    """Return the remote branches.

    Parameters
    ----------
    remote or None
        The selected remote.

    Returns
    -------
    list of str
        The remote branch names.
    """
    if remote is None:
        return []
    return [
        ref.name.replace(f"{remote}/", "")
        for ref in remote.refs
        if not ref.name.endswith("HEAD")
    ]


def repo_branch_names(repo: git.Repo, remote: Optional[git.Remote]) -> List[str]:
    """Return the local and remote branches.

    Parameters
    ----------
    repo
        The current git repository.
    remote or None
        The selected remote.

    Returns
    -------
    list of str
        The local and remote branches.
    """
    return list({*local_branch_names(repo), *remote_branch_names(remote)})


def current_branch_name(repo: git.Repo) -> Optional[str]:
    """Return the current branch name.

    Parameters
    ----------
    repo
        The current git repository.

    Returns
    -------
    str or None
        The current branch name or None if detached.
    """
    try:
        return repo.active_branch.name
    except TypeError:
        return None


class RefPosition(enum.Enum):
    """The position of a ref in comparison to a base ref."""

    AHEAD = enum.auto()
    """If the ref is ahead of the base ref."""
    EQUAL = enum.auto()
    """If the ref and the base ref are the same."""
    BEHIND = enum.auto()
    """If the ref is behind of the base ref."""
    UNRELATED = enum.auto()
    """If the ref and the base ref does not share the same history."""


def compare_ref(
    ref: git.SymbolicReference, base_ref: git.SymbolicReference
) -> RefPosition:
    """Compare a ref to a base ref and return the relative position.

    Parameters
    ----------
    ref
        The ref to be compared.
    base_ref
        The base ref of the comparison.

    Returns
    -------
    RefPosition
        The relative position of the ref compared to the base ref.
    """
    repo = ref.repo
    ahead = sum(1 for x in repo.iter_commits(f"{base_ref}..{ref}"))
    behind = sum(1 for x in repo.iter_commits(f"{ref}..{base_ref}"))
    if ahead > 0 and behind == 0:
        return RefPosition.AHEAD
    if ahead == 0 and behind == 0:
        return RefPosition.EQUAL
    if ahead == 0 and behind > 0:
        return RefPosition.BEHIND
    return RefPosition.UNRELATED


def update_branch(branch: git.Head, remote: git.Remote, force_update: bool) -> None:
    """Update a local git branch.

    Parameters
    ----------
    branch
        The selected branch.
    remote
        The selected remote.
    force_update
        Allow forced branch update.

    Raises
    ------
    SystemExit
        If the tracking branch is invalid or if the branch cannot be updated.
    """
    if branch.name not in remote_branch_names(remote):
        logger.debug("The %s branch does not yet exist on the remote", branch)
        return

    expected_tracking_branch = remote.refs[branch.name]

    tracking_branch = branch.tracking_branch()

    if tracking_branch is None:
        logger.debug(
            "Configuring the %s branch to track %s", branch, expected_tracking_branch
        )
        branch.set_tracking_branch(expected_tracking_branch)

    elif tracking_branch != expected_tracking_branch:
        if not force_update:
            raise SystemExit(
                f"Invalid tracking branch: {branch} is tracking "
                f"{tracking_branch} instead of {expected_tracking_branch}"
            )

        logger.warning(
            "Configuring the %s branch to track %s", branch, expected_tracking_branch
        )
        branch.set_tracking_branch(expected_tracking_branch)

    tracking_branch = expected_tracking_branch
    position = compare_ref(branch, tracking_branch)

    if position == RefPosition.EQUAL:
        logger.debug("The %s branch is up to date with %s", branch, tracking_branch)

    elif position == RefPosition.AHEAD:
        logger.debug("The %s branch is ahead of %s", branch, tracking_branch)

    elif position == RefPosition.BEHIND:
        logger.info("Updating the %s branch to match %s", branch, tracking_branch)
        branch.reference = tracking_branch.commit

    elif position == RefPosition.UNRELATED:
        if not force_update:
            raise SystemExit(
                f"Cannot update branch: {branch} and {tracking_branch}"
                "does not share the same history."
            )

        logger.warning("Forcing the %s branch to match %s", branch, tracking_branch)
        branch.reference = tracking_branch.commit


def create_branch(
    branch_name: str, default_ref: git.SymbolicReference, remote: Optional[git.Remote]
) -> git.Head:
    """Create a local branch.

    Parameters
    ----------
    branch_name
        The selected branch name.
    default_ref
        Default reference of the new branch.
    remote or None
        The selected remote.

    Returns
    -------
    git.refs.head.Head
        The newly created branch.
    """
    if remote and branch_name in remote_branch_names(remote):
        remote_branch = remote.refs[branch_name]
        new_branch = remote_branch.repo.create_head(branch_name, remote_branch)
        new_branch.set_tracking_branch(remote_branch)
    else:
        new_branch = default_ref.repo.create_head(branch_name, default_ref)

    return new_branch
