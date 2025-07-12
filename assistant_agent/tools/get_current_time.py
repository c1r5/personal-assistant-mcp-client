# tools/time_tools.py

from datetime import datetime
import pytz
from datetime import timedelta
import dateparser


def get_current_time(timezone: str = "America/Sao_Paulo") -> str:
    try:
        now = datetime.now(pytz.timezone(timezone))
        return now.strftime("It is currently %H:%M on %A, %B %d, %Y in timezone %Z.")
    except Exception as e:
        return f"Error retrieving time: {str(e)}"


def get_day_of_week(date_str: str) -> str:
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("That date falls on a %A.")
    except Exception as e:
        return f"Error parsing date: {str(e)}"


def parse_date_query(question: str) -> str:
    try:
        parsed = dateparser.parse(question, settings={"PREFER_DATES_FROM": "future"})
        if not parsed:
            return "Could not understand the date."
        return parsed.strftime("That is %A, %B %d, %Y.")
    except Exception as e:
        return f"Error parsing question: {str(e)}"


def calculate_future_date(days: int = 0, weeks: int = 0) -> str:
    """
    Calculates a future date by adding days and/or weeks to the current date.
    """
    future = datetime.now() + timedelta(days=days + weeks * 7)
    return future.strftime("That will be a %A, %B %d, %Y.")
