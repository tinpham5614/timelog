# main.py
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import typer
from rich import print
import csv

from db import init_db, SessionLocal, TimeSession
from helpers import (
    calculate_duration,
    format_datetime,
    format_time,
    to_local_time,
)

app = typer.Typer()
init_db()

PROJECTS = {1: "Project 1", 2: "Project 2", 3: "Project 3"}


@app.command()
def start(
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Choose a project"
    ),
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Describe the task"),
):
    """Start a new time tracking session."""
    # Project selection/validation
    print("=" * 50)
    if not project:
        print("📁 Available projects:")
        for key, value in PROJECTS.items():
            print(f"{key} - {value}")

        while True:
            try:
                selection = int(typer.prompt("Select a project (number)"))
                if selection in PROJECTS:
                    project = PROJECTS[selection]
                    break
                else:
                    print(f"[red]❌ Invalid choice. Please enter 1-{len(PROJECTS)}")
            except ValueError:
                print("[red]❌ Please enter a number")

    # Task input
    if not task:
        task = typer.prompt("Description", default="general work")

    db = SessionLocal()
    try:
        # Check for the existing active session
        active_session = (
            db.query(TimeSession).filter(TimeSession.end_time == None).first()
        )
        if active_session:
            print(
                f"[yellow]⚠️  An active session already exists: [{active_session.project}] - {active_session.task}"
            )
            if not typer.confirm("Stop it and start a new one?"):
                db.close()
                return
            active_session.end_time = datetime.now(tz=timezone.utc)
            db.commit()

        new_session = TimeSession(
            project=project,
            task=task,
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        start_display = format_datetime(to_local_time(new_session.start_time))
        print(
            f"✅ [bold]Started session: [bold][{new_session.project}] - {new_session.task}"
        )
        print(f"⏱️ Start time: {start_display}")
    except Exception as e:
        print(f"[red]❌ Error starting session: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def stop():
    """Stop the currently active time tracking session."""
    print("=" * 50)
    db = SessionLocal()
    try:
        session = (
            db.query(TimeSession)
            .filter(TimeSession.end_time == None)
            .order_by(TimeSession.start_time.desc())
            .first()
        )

        if not session:
            print("[yellow]⚠️  No active session to stop.")
            return

        session.end_time = datetime.now(tz=timezone.utc)
        db.commit()

        duration_str = calculate_duration(
            start_time=session.start_time, end_time=session.end_time or None
        )

        start_display = format_datetime(to_local_time(session.start_time))
        end_display = format_datetime(to_local_time(session.end_time))

        print(f"✅ [bold]Stopped session: [bold][{session.project}] - {session.task}")
        print(f"⏱️ Start time: {start_display}")
        print(f"⏱️ End time  : {end_display}")
        print(f"⏱️ Duration : [green]{duration_str}")
    except Exception as e:
        print(f"❌ Error stopping session: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def current():
    """Show the current session."""
    print("=" * 50)
    db = SessionLocal()
    try:
        session = db.query(TimeSession).filter(TimeSession.end_time == None).first()

        if session:
            duration_str = calculate_duration(
                start_time=session.start_time, end_time=session.end_time or None
            )
            start_display = format_datetime(to_local_time(session.start_time))

            end_display = (
                "⏳[green]ACTIVE"
                if not session.end_time
                else format_time(to_local_time(session.end_time).time())
            )
            print(f"📌 [bold]Current Session: [{session.project}] - {session.task}")
            print(f"⏱️ Start time: {start_display}")
            print(f"⏱️ End time  : {end_display}")
            print(f"⏱️ Duration : [green]{duration_str}")

        else:
            print("ℹ️ [yellow] No active session found.")
    except Exception as e:
        print(f"❌ [red]Error fetching current session: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def summary(
    today: bool = typer.Option(
        False, "--today", "-t", help="Show today's sessions only"
    ),
    week: bool = typer.Option(
        False, "--week", "-w", help="Show this week's sessions only"
    ),
):
    """
    Show a summary of all time tracking sessions.
    Add --today or -t to filter sessions started today.
    Add --week or -w to filter sessions started this week.
    """
    print("=" * 50)
    db = SessionLocal()

    try:
        if today:
            print("📅 [bold]Today's Sessions Summary (only sessions started today):")
            start_of_day = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0
            )
            sessions = (
                db.query(TimeSession)
                .filter(TimeSession.start_time >= start_of_day)
                .all()
            )
        elif week:
            print(
                "📅 [bold]This Week's Sessions Summary (only sessions started this week):"
            )
            start_of_week = datetime.now(timezone.utc) - timedelta(
                days=datetime.now(timezone.utc).weekday()
            )
            sessions = (
                db.query(TimeSession)
                .filter(TimeSession.start_time >= start_of_week)
                .all()
            )
        else:
            print("📅 [bold]All Sessions Summary:")
            sessions = db.query(TimeSession).all()

        if not sessions:
            print("[yellow]No sessions found.")
            return

        for session in sessions:
            duration_str = (
                calculate_duration(
                    start_time=session.start_time, end_time=session.end_time
                )
                if session.end_time
                else "RUNNING"
            )
            start_display = format_datetime(to_local_time(session.start_time))
            end_display = (
                format_datetime(to_local_time(session.end_time))
                if session.end_time
                else "N/A"
            )
            print(
                f"{session.id:<3} {start_display} - {end_display} {session.project:<10} - {session.task:<30} {duration_str}"
            )
    except Exception as e:
        print(f"❌ [red]Error fetching sessions: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def remove(
    session_id: int = typer.Argument(..., help="ID of session to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        prompt="Are you sure you want to delete this session?",
        help="Skip confirmation prompt",
    ),
):
    """Remove a time tracking session by ID."""
    if not session_id:
        print("[red]❌ Session ID is required")
        raise typer.Exit(code=1)
    if session_id <= 0:
        print("[red]❌ Session ID must be a positive integer")
        raise typer.Exit(code=1)
    if not isinstance(session_id, int):
        print("[red]❌ Session ID must be an integer")
        raise typer.Exit(code=1)

    print("=" * 50)
    db = SessionLocal()
    try:
        session = db.get(TimeSession, session_id)
        if not session:
            print(f"[red]❌ Session {session_id} not found")
            raise typer.Exit(code=1)

        if force or typer.confirm(
            print(
                f"Deleting session: {session_id} ({session.project} - {session.task})"
            )
        ):
            db.delete(session)
            db.commit()
            print(f"✅ [bold]Deleted session {session_id}")
        else:
            print("🟡 Deletion cancelled")
    except Exception as e:
        db.rollback()
        print(f"❌ [red]Error deleting session: {e}")
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def export(
    today: bool = typer.Option(
        False, "--today", "-t", help="Export sessions for today only"
    ),
    week: bool = typer.Option(
        False, "--week", "-w", help="Export sessions for the current week"
    ),
    start_date: Optional[str] = typer.Option(
        None, "--start", "-s", help="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "-e", help="End date in YYYY-MM-DD format"
    ),
):
    """Export all sessions to a CSV file."""
    print("=" * 50)
    db = SessionLocal()
    try:
        if today:
            start_of_day = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0
            )
            sessions = (
                db.query(TimeSession)
                .filter(TimeSession.start_time >= start_of_day)
                .all()
            )
        elif week:
            start_of_week = datetime.now(timezone.utc) - timedelta(
                days=datetime.now(timezone.utc).weekday()
            )
            sessions = (
                db.query(TimeSession)
                .filter(TimeSession.start_time >= start_of_week)
                .all()
            )
        elif start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                sessions = (
                    db.query(TimeSession)
                    .filter(
                        TimeSession.start_time >= start_dt,
                        TimeSession.start_time <= end_dt,
                    )
                    .all()
                )
            except ValueError:
                print("[red]❌ Invalid date format. Use YYYY-MM-DD.")
                raise typer.Exit(code=1)
        else:
            # Default to all sessions if no filters are applied
            sessions = db.query(TimeSession).all()
        if not sessions:
            print("[yellow]No sessions to export.")
            return

        EXPORT_DIR = Path.home() / "Desktop/timelog_exports"
        EXPORT_DIR.mkdir(exist_ok=True)
        filename = (
            EXPORT_DIR
            / f"sessions_{to_local_time(datetime.now(timezone.utc)).date().strftime('%m-%d-%Y')}.csv"
        )
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Exported on", format_datetime(to_local_time(datetime.now()))]
            )
            writer.writerow(
                ["ID", "Project", "Task", "Start Time", "End Time", "Duration"]
            )
            for session in sessions:
                duration_str = (
                    calculate_duration(
                        start_time=session.start_time, end_time=session.end_time
                    )
                    if session.end_time
                    else "RUNNING"
                )
                writer.writerow(
                    [
                        session.id,
                        session.project,
                        session.task,
                        format_datetime(to_local_time(session.start_time)),
                        format_datetime(to_local_time(session.end_time))
                        if session.end_time
                        else "N/A",
                        duration_str,
                    ]
                )
            print(f"✅ [bold]Exported {len(sessions)} sessions to {filename}")
    except Exception as e:
        print(f"❌ Error exporting sessions: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


if __name__ == "__main__":
    app()
