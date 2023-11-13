"""Test cases for the CLI."""
import logging
from pathlib import Path

import pytest

from project_release.file import EditedVersionFile
from project_release.file import FormattedVersionFile
from project_release.file import PlainVersionFile
from project_release.file import VersionEmptyError
from project_release.file import VersionInconsistentError
from project_release.file import VersionNotFoundError

logger = logging.getLogger(__name__)


class TestPlainVersionFile:
    """Test cases related to the plain version file."""

    def test_write(self, tmp_path: Path) -> None:
        """Test that a file can be write."""
        version = "1.2.3"
        path = tmp_path / "VERSION"
        file = PlainVersionFile(path)
        file.version = version
        with open(path, encoding="utf-8") as stream:
            assert stream.read() == version

    def test_read(self, tmp_path: Path) -> None:
        """Test that a valid file can be read."""
        version = "1.2.3"
        path = tmp_path / "VERSION"
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(version)
        file = PlainVersionFile(path)
        assert file.version == version

    def test_read_none(self, tmp_path: Path) -> None:
        """Test that an empty file returns nothing."""
        path = tmp_path / "VERSION"
        with open(path, "w", encoding="utf-8") as stream:
            stream.write("")
        file = PlainVersionFile(path)
        with pytest.raises(VersionEmptyError):
            logger.info(file.version)


class TestFormattedVersionFile:
    """Test cases related to the formatted version file."""

    FORMAT = """
    This is a test version file
    ---------------------------
    Here is the version: %(version)s
    Here is the second version: %(version)s
    """

    def __create_version_file(self, path: Path, version: str) -> None:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(self.FORMAT % {"version": version})

    def __check_version_file(self, path: Path, version: str) -> None:
        with open(path, encoding="utf-8") as stream:
            assert stream.read() == self.FORMAT % {"version": version}

    FORMAT_2 = """
    This is a test version file
    ---------------------------
    Here is the version: %(version_1)s
    Here is the second version: %(version_2)s
    """

    def __create_version_file_2(
        self, path: Path, version_1: str, version_2: str
    ) -> None:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(
                self.FORMAT_2 % {"version_1": version_1, "version_2": version_2}
            )

    def test_write(self, tmp_path: Path) -> None:
        """Test that a file can be write."""
        version = "1.2.3"
        path = tmp_path / "VERSION"
        file = FormattedVersionFile(path, self.FORMAT)
        file.version = version
        self.__check_version_file(path, version)

    def test_read(self, tmp_path: Path) -> None:
        """Test that a valid file can be read."""
        version = "1.2.3"
        path = tmp_path / "VERSION"
        self.__create_version_file(path, version)
        file = FormattedVersionFile(path, self.FORMAT)
        assert file.version == version

    def test_read_none(self, tmp_path: Path) -> None:
        """Test that an empty file returns nothing."""
        path = tmp_path / "VERSION"
        with open(path, "w", encoding="utf-8") as stream:
            stream.write("")
        file = FormattedVersionFile(path, self.FORMAT)
        with pytest.raises(VersionNotFoundError):
            logger.info(file.version)

    def test_read_inconsistent(self, tmp_path: Path) -> None:
        """Test that a file with inconsistent versions returns nothing."""
        version_1 = "1.2.3"
        version_2 = "2.4.6"
        path = tmp_path / "VERSION"
        self.__create_version_file_2(path, version_1, version_2)
        file = FormattedVersionFile(path, self.FORMAT)
        with pytest.raises(VersionInconsistentError):
            logger.info(file.version)

    def test_read_empty(self, tmp_path: Path) -> None:
        """Test that a file with empty versions returns nothing."""
        version = ""
        path = tmp_path / "VERSION"
        self.__create_version_file(path, version)
        file = FormattedVersionFile(path, self.FORMAT)
        with pytest.raises(VersionEmptyError):
            logger.info(file.version)


class TestEditedVersionFile:
    """Test cases related to the edited version file."""

    PATTERN = r"(?<=version: )\S*"

    FORMAT = """
    This is a test version file
    ---------------------------
    Here is the first version: %(version_1)s
    Here is the second version: %(version_2)s
    Here is an out pattern version like this: %(version_3)s
    """

    def __create_version_file(self, path: Path, version_1: str, version_2: str) -> None:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(
                self.FORMAT
                % {
                    "version_1": version_1,
                    "version_2": version_2,
                    "version_3": version_1,
                }
            )

    def __check_version_file(
        self, path: Path, version_1: str, version_2: str, version_3: str
    ) -> None:
        with open(path, encoding="utf-8") as stream:
            assert stream.read() == self.FORMAT % {
                "version_1": version_1,
                "version_2": version_2,
                "version_3": version_3,
            }

    def test_write(self, tmp_path: Path) -> None:
        """Test that a valid file can be write."""
        before_version = "1.2.3"
        after_version = "3.2.1"
        path = tmp_path / "VERSION"
        self.__create_version_file(path, before_version, before_version)
        file = EditedVersionFile(path, self.PATTERN)
        file.version = after_version
        self.__check_version_file(path, after_version, after_version, before_version)

    def test_write_inconsistent(self, tmp_path: Path) -> None:
        """Test that a file with inconsistent versions can be write."""
        before_version_1 = "1.2.3"
        before_version_2 = "2.4.6"
        after_version = "3.2.1"
        path = tmp_path / "VERSION"
        self.__create_version_file(path, before_version_1, before_version_2)
        file = EditedVersionFile(path, self.PATTERN)
        file.version = after_version
        self.__check_version_file(path, after_version, after_version, before_version_1)

    def test_read(self, tmp_path: Path) -> None:
        """Test that a valid file can be read."""
        version = "1.2.3"
        path = tmp_path / "VERSION"
        self.__create_version_file(path, version, version)
        file = EditedVersionFile(path, self.PATTERN)
        assert file.version == version

    def test_read_none(self, tmp_path: Path) -> None:
        """Test that an empty file returns nothing."""
        path = tmp_path / "VERSION"
        with open(path, "w", encoding="utf-8") as stream:
            stream.write("")
        file = EditedVersionFile(path, self.PATTERN)
        with pytest.raises(VersionNotFoundError):
            logger.info(file.version)

    def test_read_inconsistent(self, tmp_path: Path) -> None:
        """Test that a file with inconsistent versions returns nothing."""
        version_1 = "1.2.3"
        version_2 = "2.4.6"
        path = tmp_path / "VERSION"
        self.__create_version_file(path, version_1, version_2)
        file = EditedVersionFile(path, self.PATTERN)
        with pytest.raises(VersionInconsistentError):
            logger.info(file.version)

    def test_read_empty(self, tmp_path: Path) -> None:
        """Test that a file with empty versions returns nothing."""
        version = ""
        path = tmp_path / "VERSION"
        self.__create_version_file(path, version, version)
        file = EditedVersionFile(path, self.PATTERN)
        with pytest.raises(VersionEmptyError):
            logger.info(file.version)
