"""Test cases for the convention module."""
from project_release.convention import Pep440Convention
from project_release.convention import SemverConvention


class TestSemverConvention:
    """Test cases related to the semver convention."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert SemverConvention().is_valid("1.2.3+devel")

    def test_invalid(self) -> None:
        """Test that an invalid version is invalid."""
        assert not SemverConvention().is_valid("1.2.3.dev1")


class TestPep440Convention:
    """Test cases related to the pep440 convention."""

    def test_valid(self) -> None:
        """Test that a valid version is valid."""
        assert Pep440Convention().is_valid("1.2.3.dev1")

    def test_invalid(self) -> None:
        """Test that an invalid version is invalid."""
        assert not Pep440Convention().is_valid("1.2.3+devel")
