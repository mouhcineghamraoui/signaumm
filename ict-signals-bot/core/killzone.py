"""
ICT Killzone filter.
Signals are highest-probability during specific session windows.
Times are in UTC.

  London Killzone : 07:00 - 10:00 UTC
  New York Killzone: 12:00 - 15:00 UTC
  (Asian range usually avoided for entries)
"""

from datetime import datetime, timezone

KILLZONES = {
    "london": (7, 10),
    "newyork": (12, 15),
}


def in_killzone(dt: datetime = None, zones=("london", "newyork")) -> bool:
    """Return True if current UTC time falls in an enabled killzone."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    hour = dt.hour
    for z in zones:
        start, end = KILLZONES[z]
        if start <= hour < end:
            return True
    return False


def active_killzone(dt: datetime = None):
    """Return name of active killzone or None."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    hour = dt.hour
    for name, (start, end) in KILLZONES.items():
        if start <= hour < end:
            return name
    return None
