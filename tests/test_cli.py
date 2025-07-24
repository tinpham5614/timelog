from typer.testing import CliRunner
from main import app

runner = CliRunner()


def test_start_new_session():
    result = runner.invoke(app, ["start", "--project", "Test", "--task", "testing"])
    assert "Test" in result.stdout
    assert "Started session" in result.stdout
    assert result.exit_code == 0


def test_current_command():
    runner.invoke(app, ["start", "--project", "Current", "--task", "testing"])
    result = runner.invoke(app, ["current"])
    assert "Current" in result.stdout
    assert "Start time" in result.stdout
    assert result.exit_code == 0
    runner.invoke(app, ["stop"])


def test_stop_command():
    runner.invoke(app, ["start", "--project", "StopTest", "--task", "testing"])
    result = runner.invoke(app, ["stop"])
    assert result.exit_code == 0
    assert "Stopped session" in result.stdout


def test_summary_command():
    runner.invoke(app, ["stop"])
    runner.invoke(app, ["start", "--project", "SummaryTest", "--task", "testing"])
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "SummaryTest" in result.stdout


def test_remove_command():
    runner.invoke(app, ["start", "--project", "RemoveTest", "--task", "testing"])
    result = runner.invoke(app, ["remove", "1", "-f"])
    assert result.exit_code == 0
    assert "Deleted session" in result.stdout


def test_export_command():
    runner.invoke(app, ["start", "--project", "ExportTest", "--task", "testing"])
    result = runner.invoke(app, ["export"])
    assert result.exit_code == 0
    assert "Exported" in result.stdout
    assert "sessions to" in result.stdout
    runner.invoke(app, ["stop"])
