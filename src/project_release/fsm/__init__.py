"""A Finite State Machine."""

import logging
from pathlib import Path
from typing import Optional

import git

logger = logging.getLogger(__name__)


class FiniteStateMachine:
    def __init__(self, repo: git.Repo) -> None:
        pass

    def status(self) -> None:
        pass

    def abort(self) -> None:
        pass

    def is_configured(self) -> bool:
        return True

    def cnotinue(self) -> None:
        pass

    def configure(self, filename: Optional[Path]) -> None:
        pass

    def run(self) -> None:
        pass
