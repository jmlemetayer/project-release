"""Conventions related code."""
import abc
import logging

import pep440
import semver

logger = logging.getLogger(__name__)


class InvalidVersionError(Exception):
    """Invalid version string."""


class VersionConvention(abc.ABC):
    """An abstract class to handle a version convention."""

    @abc.abstractmethod
    def is_valid(self, version: str) -> bool:
        """Validate a version string.

        Parameters
        ----------
        version: str
            The version string.

        Returns
        -------
        bool
            Is the provided version string valid?

        Raises
        ------
        InvalidVersionError
            If the version string is invalid.
        """
        raise NotImplementedError


class SemverConvention(VersionConvention):
    """Semantic Versioning version convention.

    Notes
    -----
    - `Semantic Versioning`_

    .. _Semantic Versioning: https://semver.org
    """

    def is_valid(self, version: str) -> bool:
        """Validate a semver version string.

        See Also
        --------
        VersionConvention.is_valid
        """
        try:
            semver.VersionInfo.parse(version)
            return True
        except ValueError as err:
            raise InvalidVersionError(
                f"Invalid semver version string: '{version}'"
            ) from err


class Pep440Convention(VersionConvention):
    """PEP 440 version convention.

    Notes
    -----
    - `PEP 440`_

    .. _PEP 440: https://peps.python.org/pep-0440/
    """

    def is_valid(self, version: str) -> bool:
        """Validate a pep440 version string.

        See Also
        --------
        VersionConvention.is_valid
        """
        if not pep440.is_canonical(version):
            raise InvalidVersionError(f"Invalid pep440 version string: '{version}'")
        return True
