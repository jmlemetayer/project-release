"""Test cases for the config."""
import logging
from pathlib import Path
from typing import Any

import pytest
import schema
import yaml
from project_release.config import Config
from project_release.file import EditedVersionFile
from project_release.file import FormattedVersionFile
from project_release.file import PlainVersionFile
from project_release.validation import AcceptAllValidator
from project_release.validation import Pep440Validator
from project_release.validation import SemverValidator

logger = logging.getLogger(__name__)


class TestConfig:  # pylint: disable=too-few-public-methods
    """Base class for the config tests."""

    def write_yaml(self, path: Path, data: Any) -> Path:
        """Format and write data as yaml into a file."""
        filename = path / "config.yaml"
        with open(filename, "w", encoding="utf-8") as stream:
            stream.write(yaml.safe_dump(data))
        return filename


class TestValidationConfig(TestConfig):
    """Test cases related to the 'validation' config."""

    def test_no_validation(self, tmp_path: Path) -> None:
        """Test that a config without 'validation' is valid."""
        path = self.write_yaml(tmp_path, {})
        config = Config(path)
        config.parse()
        assert isinstance(config["version_validator"], AcceptAllValidator)

    def test_no_version(self, tmp_path: Path) -> None:
        """Test that a config without 'version' is valid."""
        path = self.write_yaml(tmp_path, {"validation": {}})
        config = Config(path)
        config.parse()
        assert isinstance(config["version_validator"], AcceptAllValidator)

    def test_version_semver(self, tmp_path: Path) -> None:
        """Test that a config with 'version=semver' is valid."""
        path = self.write_yaml(tmp_path, {"validation": {"version": "semver"}})
        config = Config(path)
        config.parse()
        assert isinstance(config["version_validator"], SemverValidator)

    def test_version_pep440(self, tmp_path: Path) -> None:
        """Test that a config with 'version=pep440' is valid."""
        path = self.write_yaml(tmp_path, {"validation": {"version": "pep440"}})
        config = Config(path)
        config.parse()
        assert isinstance(config["version_validator"], Pep440Validator)

    def test_version_invalid(self, tmp_path: Path) -> None:
        """Test that a config with 'version=invalid' is invalid."""
        path = self.write_yaml(tmp_path, {"validation": {"version": "invalid"}})
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
        assert not config["version_files"]

    def test_no_version(self, tmp_path: Path) -> None:
        """Test that a config without 'version' is valid."""
        path = self.write_yaml(tmp_path, {"file": {}})
        config = Config(path)
        config.parse()
        assert not config["version_files"]

    def test_version(self, tmp_path: Path) -> None:
        """Test that a config with 'version' as 'str' is valid."""
        path = self.write_yaml(tmp_path, {"file": {"version": "path"}})
        config = Config(path)
        config.parse()
        assert len(config["version_files"]) == 1
        assert isinstance(config["version_files"][0], PlainVersionFile)

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
        assert len(config["version_files"]) == 1
        assert isinstance(config["version_files"][0], PlainVersionFile)

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
        assert len(config["version_files"]) == 1
        assert isinstance(config["version_files"][0], FormattedVersionFile)

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
        assert len(config["version_files"]) == 1
        assert isinstance(config["version_files"][0], EditedVersionFile)

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
        assert len(config["version_files"]) == 4
        assert isinstance(config["version_files"][0], PlainVersionFile)
        assert isinstance(config["version_files"][1], PlainVersionFile)
        assert isinstance(config["version_files"][2], FormattedVersionFile)
        assert isinstance(config["version_files"][3], EditedVersionFile)
