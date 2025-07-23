from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Los_Angeles")


def make_aware(input_datetime: datetime) -> datetime:
    """Make datetime to be aware with utc timezone."""
    if not input_datetime.tzinfo:
        utc_time = input_datetime.replace(tzinfo=timezone.utc)
    return utc_time


def to_local_time(utc_time: datetime) -> datetime:
    """Convert utc datetime to local date time."""
    if not utc_time.tzinfo:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    return utc_time.astimezone(LOCAL_TZ)


def format_datetime(local_datetime: datetime) -> str:
    """Format local date time in format: mm-dd-yyyy hh:mm:ss."""
    if not local_datetime:
        return

    return local_datetime.strftime("%m-%d-%Y %H:%M:%S")


def format_time(time: time) -> str:
    """Format time in format: hh:mm:ss."""
    if not time:
        return
    return time.strftime("%H:%M:%S")


def calculate_duration(start_time: datetime, end_time) -> str:
    """Calculate duration given start time and end time."""
    end_time = make_aware(end_time) if end_time else datetime.now(tz=timezone.utc)
    duration = end_time - make_aware(start_time)
    total_seconds = duration.total_seconds()
    hours = total_seconds / 3600
    minutes = (hours % 1) * 60

    if hours > 1:
        duration_str = f"{int(hours)}h {round(minutes)}m"
    else:
        duration_str = f"{round(minutes)}m"
    return duration_str
