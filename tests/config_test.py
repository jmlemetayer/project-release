"""Test cases for the config."""
import logging
from pathlib import Path
from typing import Any

import pytest
import schema
import yaml
from project_release.config import Config
from project_release.convention import Pep440Convention
from project_release.convention import SemverConvention
from project_release.file import EditedVersionFile
from project_release.file import FormattedVersionFile
from project_release.file import PlainVersionFile

logger = logging.getLogger(__name__)


class TestConfig:  # pylint: disable=too-few-public-methods
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
        config = Config(path)
        config.parse()
        assert config.convention.version is None

    def test_no_version(self, tmp_path: Path) -> None:
        """Test that a config without 'version' is valid."""
        path = self.write_yaml(tmp_path, {"convention": {}})
        config = Config(path)
        config.parse()
        assert config.convention.version is None

    def test_version_semver(self, tmp_path: Path) -> None:
        """Test that a config with 'version=semver' is valid."""
        path = self.write_yaml(tmp_path, {"convention": {"version": "semver"}})
        config = Config(path)
        config.parse()
        assert isinstance(config.convention.version, SemverConvention)

    def test_version_pep440(self, tmp_path: Path) -> None:
        """Test that a config with 'version=pep440' is valid."""
        path = self.write_yaml(tmp_path, {"convention": {"version": "pep440"}})
        config = Config(path)
        config.parse()
        assert isinstance(config.convention.version, Pep440Convention)

    def test_version_invalid(self, tmp_path: Path) -> None:
        """Test that a config with 'version=invalid' is invalid."""
        path = self.write_yaml(tmp_path, {"convention": {"version": "invalid"}})
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()


class TestFileConfig(TestConfig):
    """Test cases related to the 'file' config."""

    def test_no_file(self, tmp_path: Path) -> None:
        """Test that a config without 'file' is valid."""
        path = self.write_yaml(tmp_path, {})
        config = Config(path)
        config.parse()
        assert not config.file.version

    def test_no_version(self, tmp_path: Path) -> None:
        """Test that a config without 'version' is valid."""
        path = self.write_yaml(tmp_path, {"file": {}})
        config = Config(path)
        config.parse()
        assert not config.file.version

    def test_version(self, tmp_path: Path) -> None:
        """Test that a config with 'version' as 'str' is valid."""
        path = self.write_yaml(tmp_path, {"file": {"version": "path"}})
        config = Config(path)
        config.parse()
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], PlainVersionFile)

    def test_version_not_dict(self, tmp_path: Path) -> None:
        """Test that a config with 'version' not as 'dict' is invalid."""
        path = self.write_yaml(tmp_path, {"file": {"version": 1234}})
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()

    def test_version_no_path(self, tmp_path: Path) -> None:
        """Test that a config without 'path' is invalid."""
        path = self.write_yaml(tmp_path, {"file": {"version": {}}})
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()

    def test_version_path_not_str(self, tmp_path: Path) -> None:
        """Test that a config with 'path' not as 'str' is invalid."""
        path = self.write_yaml(tmp_path, {"file": {"version": {"path": 1234}}})
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()

    def test_version_path(self, tmp_path: Path) -> None:
        """Test that a config with 'path' as 'str' is valid."""
        path = self.write_yaml(tmp_path, {"file": {"version": {"path": "path"}}})
        config = Config(path)
        config.parse()
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], PlainVersionFile)

    def test_version_format_not_str(self, tmp_path: Path) -> None:
        """Test that a config with 'format' not as 'str' is invalid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "format": 1234}}}
        )
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()

    def test_version_format(self, tmp_path: Path) -> None:
        """Test that a config with 'format' as 'str' is valid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "format": "format"}}}
        )
        config = Config(path)
        config.parse()
        assert len(config.file.version) == 1
        assert isinstance(config.file.version[0], FormattedVersionFile)

    def test_version_pattern_not_str(self, tmp_path: Path) -> None:
        """Test that a config with 'pattern' not as 'str' is invalid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "pattern": 1234}}}
        )
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()

    def test_version_pattern(self, tmp_path: Path) -> None:
        """Test that a config with 'pattern' as 'str' is valid."""
        path = self.write_yaml(
            tmp_path, {"file": {"version": {"path": "path", "pattern": "pattern"}}}
        )
        config = Config(path)
        config.parse()
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
        config = Config(path)
        with pytest.raises(schema.SchemaError):
            config.parse()

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
        config = Config(path)
        config.parse()
        assert len(config.file.version) == 4
        assert isinstance(config.file.version[0], PlainVersionFile)
        assert isinstance(config.file.version[1], PlainVersionFile)
        assert isinstance(config.file.version[2], FormattedVersionFile)
        assert isinstance(config.file.version[3], EditedVersionFile)
