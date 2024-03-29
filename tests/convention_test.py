"""Test cases for the convention module."""
import logging

from project_release.convention import AcceptAllValidator
from project_release.convention import Pep440Validator
from project_release.convention import SemverValidator

logger = logging.getLogger(__name__)


class TestAcceptAllValidator:
    """Test cases related to the accept all validator."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert AcceptAllValidator().validate_version("1.2.3+devel")
        assert AcceptAllValidator().validate_version("1.2.3.dev1")


class TestSemverValidator:
    """Test cases related to the semver validator."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert SemverValidator().validate_version("1.2.3+devel")

    def test_invalid(self) -> None:
        """Test that an invalid version is invalid."""
        assert isinstance(SemverValidator().validate_version("1.2.3.dev1"), str)


class TestPep440Validator:
    """Test cases related to the pep440 validator."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert Pep440Validator().validate_version("1.2.3.dev1")

    def test_invalid(self) -> None:
        """Test that an invalid version is invalid."""
        assert isinstance(Pep440Validator().validate_version("1.2.3+devel"), str)
