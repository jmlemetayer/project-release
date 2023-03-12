"""Validations related code."""
import abc
import logging
from typing import Union

import pep440
import semver

logger = logging.getLogger(__name__)


class VersionValidator(abc.ABC):
    """An abstract class to handle a version validator."""

    @abc.abstractmethod
    def validate(self, version: str) -> Union[bool, str]:
        """Validate a version string.

        Parameters
        ----------
        version: str
            The version string.

        Returns
        -------
        bool
            Is the provided version string valid?
        str
            Reason why the version string is not valid.
        """
        raise NotImplementedError


class AcceptAllValidator(VersionValidator):
    """Version validator that accept all."""

    def validate(self, _version: str) -> Union[bool, str]:
        """Accept all version string.

        See Also
        --------
        VersionValidator.validate
        """
        return True


class SemverValidator(VersionValidator):
    """Semantic Versioning version validator.

    Notes
    -----
    - `Semantic Versioning`_

    .. _Semantic Versioning: https://semver.org
    """

    def validate(self, version: str) -> Union[bool, str]:
        """Validate a semver version string.

        See Also
        --------
        VersionValidator.validate
        """
        try:
            semver.VersionInfo.parse(version)
            return True
        except ValueError:
            return f"Invalid semver version string: '{version}'"


class Pep440Validator(VersionValidator):
    """PEP 440 version validator.

    Notes
    -----
    - `PEP 440`_

    .. _PEP 440: https://peps.python.org/pep-0440/
    """

    def validate(self, version: str) -> Union[bool, str]:
        """Validate a pep440 version string.

        See Also
        --------
        VersionValidator.validate
        """
        if not pep440.is_canonical(version):
            return f"Invalid pep440 version string: '{version}'"
        return True
