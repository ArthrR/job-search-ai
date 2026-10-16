from typer.testing import CliRunner

from job_search_ai import __version__
from job_search_ai.cli import app

runner = CliRunner()

PIPELINE_COMMANDS = ("collect", "score", "review", "run", "eval")


def test_help_lists_every_pipeline_command():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    for command in PIPELINE_COMMANDS:
        assert command in result.output


def test_version_prints_installed_version():
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_unbuilt_stages_fail_loudly():
    for command in PIPELINE_COMMANDS:
        result = runner.invoke(app, [command])
        assert result.exit_code == 1, f"'{command}' should exit 1 until it is implemented"
