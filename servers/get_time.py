from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "get_time",
    description="A tool to get the current time in a specified timezone.",
    version="1.0.0",
)


@mcp.tool(
    name="get_current_time",
    description="Get the current time in a specific timezone (e.g. 'America/Sao_Paulo', 'Asia/Tokyo', 'Europe/London').",
)
async def get_current_time(timezone: str = "America/Sao_Paulo") -> str:
    """
    Get the current time in a specified timezone.

    Args:
        timezone: The IANA timezone to get the current time for.
                  Examples: 'America/Sao_Paulo', 'Europe/London', 'Asia/Tokyo'

    Returns:
        The current time formatted as 'YYYY-MM-DD HH:MM:SS TZ'
    """
    from datetime import datetime
    import pytz

    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except pytz.UnknownTimeZoneError:
        return f"Unknown timezone: {timezone}. Please provide a valid timezone like 'America/Sao_Paulo'."
    except Exception as e:
        return f"An error occurred: {e}"


@mcp.resource(
    name="available_timezones",
    uri="helper://timezones",
    description="List of available IANA timezones you can use, consider detect user language.",
)
def available_timezones() -> str:
    """
    List of available timezones.

    Returns:
        str: A string containing the list of available timezones.
    """
    import pytz

    return "\n".join(pytz.all_timezones)


if __name__ == "__main__":
    mcp.run("stdio")

