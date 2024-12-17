"""Time-related tools for the assistant."""

from datetime import datetime
from dateutil import tz

def get_current_datetime(timezone: str = None) -> dict:
    """Get current date and time information."""
    try:
        if timezone:
            tzinfo = tz.gettz(timezone)
            if not tzinfo:
                return {"error": f"Invalid timezone: {timezone}"}
            current = datetime.now(tzinfo)
        else:
            current = datetime.now(tz.tzlocal())
            
        return {
            "date": current.strftime("%Y-%m-%d"),
            "time": current.strftime("%H:%M:%S"),
            "timezone": str(current.tzinfo or 'local'),
            "timestamp": current.timestamp(),
            "iso_format": current.isoformat()
        }
    except Exception as e:
        return {
            "error": f"Failed to get datetime: {str(e)}"
        } 