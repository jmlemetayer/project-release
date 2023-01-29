"""Test cases for the validation module."""
import logging

import pytest
from project_release.validation import AcceptAllValidator
from project_release.validation import InvalidVersionError
from project_release.validation import Pep440Validator
from project_release.validation import SemverValidator

logger = logging.getLogger(__name__)


class TestAcceptAllValidator:
    """Test cases related to the accept all validator."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert AcceptAllValidator().validate("1.2.3+devel")
        assert AcceptAllValidator().validate("1.2.3.dev1")


class TestSemverValidator:
    """Test cases related to the semver validator."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert SemverValidator().validate("1.2.3+devel")

    def test_invalid(self) -> None:
        """Test that an invalid version is invalid."""
        with pytest.raises(InvalidVersionError):
            SemverValidator().validate("1.2.3.dev1")


class TestPep440Validator:
    """Test cases related to the pep440 validator."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert Pep440Validator().validate("1.2.3.dev1")

    def test_invalid(self) -> None:
        """Test that an invalid version is invalid."""
        with pytest.raises(InvalidVersionError):
            Pep440Validator().validate("1.2.3+devel")
