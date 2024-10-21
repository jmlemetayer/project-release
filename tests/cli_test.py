"""Test cases for the CLI."""

import pytest

from project_release import __version__
from project_release.cli import project_release_cli


class TestCli:
    """Test cases related to the CLI command."""

    def test_version(self, capsys: pytest.CaptureFixture) -> None:
        """Test the `--version` option return the version."""
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            project_release_cli(["--version"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == f"project-release {__version__}\n"
