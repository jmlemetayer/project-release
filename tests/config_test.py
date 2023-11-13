"""Test cases for the config."""
import logging
from pathlib import Path
from typing import Any

import pytest
import yaml

from project_release.config import parse_config
from project_release.convention import AcceptAllValidator
from project_release.convention import Pep440Validator
from project_release.convention import SemverValidator
from project_release.error import InvalidConfigFileError
from project_release.file import EditedVersionFile
from project_release.file import FormattedVersionFile
from project_release.file import PlainVersionFile

logger = logging.getLogger(__name__)


class TestConfig:
    """Base class for the config tests."""

    def write_yaml(self, path: Path, data: Any) -> Path:
        """Format and write data as yaml into a file."""
        filename = path / "config.yaml"
        with open(filename, "w", encoding="utf-8") as stream:
            stream.write(yaml.safe_dump(data))
        return filename


class TestConventionConfig(TestConfig):
    """Test cases related to the 'convention' config."""

    def test_no_convention(self, tmp_path: Path) -> None:
        """Test that a config without 'convention' is valid."""
        path = self.write_yaml(tmp_path, {})
        config = parse_config(path)
        assert isinstance(config.convention.version, AcceptAllValidator)

    def test_no_version(self, tmp_path: Path) -> None:
        """Test that a config without 'version' is valid."""
        path = self.write_yaml(tmp_path, {"convention": {}})
        config = parse_config(path)
        assert isinstance(config.convention.version, AcceptAllValidator)

    def test_version_semver(self, tmp_path: Path) -> None:
        """Test that a config with 'version=semver' is valid."""
        path = self.write_yaml(tmp_path, {"convention": {"version": "semver"}})
        config = parse_config(path)
        assert isinstance(config.convention.version, SemverValidator)

    def test_version_pep440(self, tmp_path: Path) -> None:
        """Test that a config with 'version=pep440' is valid."""
        path = self.write_yaml(tmp_path, {"convention": {"version": "pep440"}})
        config = parse_config(path)
        assert isinstance(config.convention.version, Pep440Validator)

    def test_version_invalid(self, tmp_path: Path) -> None:
        """Test that a config with 'version=invalid' is invalid."""
        path = self.write_yaml(tmp_path, {"convention": {"version": "invalid"}})
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)


class TestFileConfig(TestConfig):
    """Test cases related to the 'file' config."""

    def test_no_file(self, tmp_path: Path) -> None:
        """Test that a config without 'file' is valid."""
        path = self.write_yaml(tmp_path, {})
        config = parse_config(path)
        assert not config.file.version

    def test_no_version(self, tmp_path: Path) -> None:
        """Test that a config without 'version' is valid."""
        path = self.write_yaml(tmp_path, {"file": {}})
        config = parse_config(path)
        assert not config.file.version

    def test_version(self, tmp_path: Path) -> None:
        """Test that a config with 'version' as 'str' is valid."""
        path = self.write_yaml(tmp_path, {"file": {"version": "path"}})
        config = parse_config(path)
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], PlainVersionFile)

    def test_version_not_dict(self, tmp_path: Path) -> None:
        """Test that a config with 'version' not as 'dict' is invalid."""
        path = self.write_yaml(tmp_path, {"file": {"version": 1234}})
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)

    def test_version_no_path(self, tmp_path: Path) -> None:
        """Test that a config without 'path' is invalid."""
        path = self.write_yaml(tmp_path, {"file": {"version": {}}})
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)

    def test_version_path_not_str(self, tmp_path: Path) -> None:
        """Test that a config with 'path' not as 'str' is invalid."""
        path = self.write_yaml(tmp_path, {"file": {"version": {"path": 1234}}})
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)

    def test_version_path(self, tmp_path: Path) -> None:
        """Test that a config with 'path' as 'str' is valid."""
        path = self.write_yaml(tmp_path, {"file": {"version": {"path": "path"}}})
        config = parse_config(path)
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], PlainVersionFile)

    def test_version_format_not_str(self, tmp_path: Path) -> None:
        """Test that a config with 'format' not as 'str' is invalid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "format": 1234}}}
        )
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)

    def test_version_format(self, tmp_path: Path) -> None:
        """Test that a config with 'format' as 'str' is valid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "format": "format"}}}
        )
        config = parse_config(path)
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], FormattedVersionFile)

    def test_version_pattern_not_str(self, tmp_path: Path) -> None:
        """Test that a config with 'pattern' not as 'str' is invalid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "pattern": 1234}}}
        )
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)

    def test_version_pattern(self, tmp_path: Path) -> None:
        """Test that a config with 'pattern' as 'str' is valid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "pattern": "pattern"}}}
        )
        config = parse_config(path)
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], EditedVersionFile)

    def test_version_both_format_pattern(self, tmp_path: Path) -> None:
        """Test that a config with both 'format' and 'pattern' is invalid."""
        path = self.write_yaml(
            tmp_path,
            {
                "file": {
                    "version": {
                        "path": "path",
                        "format": "format",
                        "pattern": "pattern",
                    }
                }
            },
        )
        with pytest.raises(InvalidConfigFileError):
            parse_config(path)

    def test_version_list(self, tmp_path: Path) -> None:
        """Test that a config with 'version' as 'list' is valid."""
        path = self.write_yaml(
            tmp_path,
            {
                "file": {
                    "version": [
                        "path",
                        {"path": "path"},
                        {"path": "path", "format": "format"},
                        {"path": "path", "pattern": "pattern"},
                    ]
                }
            },
        )
        config = parse_config(path)
        assert len(config.file.version) == 4
        assert isinstance(config.file.version[0], PlainVersionFile)
        assert isinstance(config.file.version[1], PlainVersionFile)
        assert isinstance(config.file.version[2], FormattedVersionFile)
        assert isinstance(config.file.version[3], EditedVersionFile)
