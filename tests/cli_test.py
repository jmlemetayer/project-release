"""Test cases for the CLI."""
import logging
import os
from pathlib import Path
from typing import Any
from typing import Iterator
from typing import Optional

import pytest
import yaml
from _pytest.fixtures import FixtureRequest
from project_release import __version__
from project_release.cli import project_release_cli

logger = logging.getLogger(__name__)


class TestCli:  # pylint: disable=too-few-public-methods
    """Test cases related to the CLI command."""

    @pytest.fixture
    def test_dir(self, request: FixtureRequest, tmp_path: Path) -> Iterator[Path]:
        """A fixture that change the working directory into a temporary directory."""
        os.chdir(tmp_path)
        yield tmp_path
        os.chdir(request.config.invocation_dir)

    def write_yaml(
        self, path: Path, data: Any, config_file: Optional[str] = None
    ) -> Path:
        """Format and write data as yaml into the config file."""
        if config_file is None:
            config_file = ".project-release-config.yaml"
        filename = path / config_file
        with open(filename, "w", encoding="utf-8") as stream:
            stream.write(yaml.safe_dump(data))
        return filename.relative_to(path)

    def test_version(self, capsys: pytest.CaptureFixture) -> None:
        """Test that the `--version` option returns the version."""
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            project_release_cli(["--version"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == f"project-release {__version__}\n"

    def test_verbose(self, test_dir: Path, caplog: pytest.LogCaptureFixture) -> None:
        """Test that the `--verbose` option is valid."""
        config_file = self.write_yaml(test_dir, {})
        assert project_release_cli(["--verbose"]) == 0
        assert len(caplog.records) >= 1
        assert caplog.records[0].levelno == logging.DEBUG
        assert (
            caplog.records[0].getMessage()
            == f"Opening configuration file: '{config_file}'"
        )

    def test_no_default_config(
        self, test_dir: Path  # pylint: disable=unused-argument
    ) -> None:
        """Test that no default config file is invalid."""
        with pytest.raises(FileNotFoundError):
            project_release_cli([])

    def test_config_no_config(
        self, test_dir: Path  # pylint: disable=unused-argument
    ) -> None:
        """Test that no config file with the `--config` option is invalid."""
        with pytest.raises(FileNotFoundError):
            project_release_cli(["--config=invalid"])
