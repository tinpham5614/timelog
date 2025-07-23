# main.py
from datetime import datetime, timezone
from typing import Optional

import typer
from rich import print

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
                    print("------------------------------------")
                    print(f"[red]❌ Invalid choice. Please enter 1-{len(PROJECTS)}")
            except ValueError:
                print("------------------------------------")
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
            print("------------------------------------")
            print(
                f"[yellow]⚠️  Active session: {active_session.project} - {active_session.task}."
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
        print("------------------------------------")
        print(f"✅ Started session: [bold]{project} - {task}")
        print(f"🕒 Start time: {start_display}")
    except Exception as e:
        print(f"[red]❌ Error starting session: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def stop():
    """Stop the currently active time tracking session."""
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

        print("------------------------------------")
        print(f"🛑 Stopped session: [bold][{session.project}] - {session.task}")
        print(f"⏱️ Start time: {start_display} | End time: {end_display}")
        print(f"⏱️ Duration: [green]{duration_str}")
    except Exception as e:
        print(f"❌ Error stopping session: {e}")
        db.rollback()
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def current():
    """Show the current session."""
    db = SessionLocal()
    try:
        session = db.query(TimeSession).filter(TimeSession.end_time == None).first()

        if session:
            duration_str = calculate_duration(
                start_time=session.start_time, end_time=session.end_time or None
            )
            start_display = format_datetime(to_local_time(session.start_time))

            print("------------------------------------")
            print(f"📖 [bold][{session.project}] - {session.task}")
            print(f"🕒 Start time: {start_display}")
            print(f"🕒 Duration : [green]{duration_str}")

        else:
            print("ℹ️ [yellow] No active session found.")
    finally:
        db.close()


@app.command()
def summary():
    """Show all sessions."""
    db = SessionLocal()

    try:
        today_start = to_local_time(datetime.now(tz=timezone.utc))
        today_utc = datetime.astimezone(today_start, timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        sessions = (
            db.query(TimeSession)
            .filter(TimeSession.start_time >= today_utc)
            .order_by(TimeSession.start_time.desc())
            .all()
        )

        if not sessions:
            print("[yellow]No sessions found for today.")
            return

        for session in sessions:
            duration_str = (
                "RUNNING"
                if not session.end_time
                else calculate_duration(
                    start_time=session.start_time, end_time=session.end_time
                )
            )

            start_display = format_datetime(to_local_time(session.start_time))
            end_display = (
                "STILL ACTIVE"
                if not session.end_time
                else format_time(to_local_time(session.end_time).time())
            )

            print(
                f"{start_display} - {end_display} | "
                f"[{session.project}] - {session.task} | "
                f"{duration_str}",
            )
    finally:
        db.close()


if __name__ == "__main__":
    app()
