"""Conventions related code."""
import logging
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import Optional
from typing import Union

import pep440
import semver
from pydantic import BaseModel
from pydantic import field_validator
from pydantic import model_serializer
from pydantic import validate_call

from ._pydantic import UseDefaultValueModel

logger = logging.getLogger(__name__)


class VersionValidator(ABC, BaseModel):
    """An abstract class to handle a version validator."""

    @abstractmethod
    def validate_version(self, version: str) -> Union[bool, str]:
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

    @model_serializer
    def serialize(self) -> str:
        """Generate a dictionary representation of the model."""
        return self._serialize()

    @abstractmethod
    def _serialize(self) -> str:
        raise NotImplementedError


class AcceptAllValidator(VersionValidator):
    """Version validator that accept all."""

    def validate_version(self, _version: str) -> Union[bool, str]:
        """Accept all version string.

        See Also
        --------
        VersionValidator.validate_version
        """
        return True

    def _serialize(self) -> str:
        return "all"


class SemverValidator(VersionValidator):
    """Semantic Versioning version validator.

    Notes
    -----
    - `Semantic Versioning`_

    .. _Semantic Versioning: https://semver.org
    """

    def validate_version(self, version: str) -> Union[bool, str]:
        """Validate a semver version string.

        See Also
        --------
        VersionValidator.validate_version
        """
        try:
            semver.VersionInfo.parse(version)
            return True
        except ValueError:
            return f"Invalid semver version string: '{version}'"

    def _serialize(self) -> str:
        return "semver"


class Pep440Validator(VersionValidator):
    """PEP 440 version validator.

    Notes
    -----
    - `PEP 440`_

    .. _PEP 440: https://peps.python.org/pep-0440/
    """

    def validate_version(self, version: str) -> Union[bool, str]:
        """Validate a pep440 version string.

        See Also
        --------
        VersionValidator.validate_version
        """
        if not pep440.is_canonical(version):
            return f"Invalid pep440 version string: '{version}'"
        return True

    def _serialize(self) -> str:
        return "pep440"


class VersionValidatorEnum(str, Enum):
    """The available version validators."""

    ALL = "all"
    SEMVER = "semver"
    PEP440 = "pep440"

    @classmethod
    def _missing_(cls, value: Any) -> Optional["VersionValidatorEnum"]:
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        return None


class ConventionConfig(UseDefaultValueModel):
    """Convention configuration."""

    version: VersionValidator = AcceptAllValidator()

    @field_validator("version", mode="before")
    @classmethod
    @validate_call
    def _validate_version(
        cls, value: Optional[VersionValidatorEnum]
    ) -> VersionValidator:
        """Validate the version field."""
        if value is None:
            return AcceptAllValidator()
        version_validator = VersionValidatorEnum(value)
        if version_validator == VersionValidatorEnum.SEMVER:
            return SemverValidator()
        if version_validator == VersionValidatorEnum.PEP440:
            return Pep440Validator()
        return AcceptAllValidator()
