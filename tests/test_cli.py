from typer.testing import CliRunner
from main import app
import pytest

runner = CliRunner()


def test_start_new_session():
    # Clean up first
    runner.invoke(app, ["stop"])

    result = runner.invoke(app, ["start", "--project", "Test", "--task", "testing"])
    assert "Test" in result.stdout
    assert "Started session" in result.stdout
    assert result.exit_code == 0


def test_current_command():
    # Start a session first
    runner.invoke(app, ["start", "--project", "Current", "--task", "testing"])
    result = runner.invoke(app, ["current"])
    assert "Current" in result.stdout
    assert "Start time" in result.stdout
    assert result.exit_code == 0
    # Clean up
    runner.invoke(app, ["stop"])


def test_stop_command():
    # Start a session first
    runner.invoke(app, ["start", "--project", "StopTest", "--task", "testing"])
    result = runner.invoke(app, ["stop"])
    assert result.exit_code == 0
    assert "Stopped session" in result.stdout


def test_summary_command():
    # Clean up first
    runner.invoke(app, ["stop"])
    # Start new session
    runner.invoke(app, ["start", "--project", "SummaryTest", "--task", "testing"])
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "SummaryTest" in result.stdout


def test_remove_command():
    runner.invoke(app, ["start", "--project", "RemoveTest", "--task", "testing"])
    result = runner.invoke(app, ["remove", "1", "-f"])
    assert result.exit_code == 0
    assert "Deleted session" in result.stdout
