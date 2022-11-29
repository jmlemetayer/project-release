"""Test cases for the convention module."""
from project_release.convention import Pep440Convention
from project_release.convention import SemverConvention


def test_version_semver_valid() -> None:
    """Test that a valid semver version is valid."""
    assert SemverConvention().is_valid("1.2.3+devel")


def test_version_semver_invalid() -> None:
    """Test that an invalid semver version is invalid."""
    assert not SemverConvention().is_valid("1.2.3.dev1")


def test_version_pep440_valid() -> None:
    """Test that a valid pep440 version is valid."""
    assert Pep440Convention().is_valid("1.2.3.dev1")


def test_version_pep440_invalid() -> None:
    """Test that an invalid pep440 version is invalid."""
    assert not Pep440Convention().is_valid("1.2.3+devel")
