"""Utils."""

from datetime import date, datetime, timedelta
from .models import Fixture

def get_week_dates() -> tuple[str, str]:
    """Return the start and end dates in string format for the current week."""

    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return str(start), str(end)

def calculate_next_fixture(fixtures: list[Fixture], selected_date: datetime) -> Fixture:
    """Return the next upcoming fixture given a datetime object. If a fixture can't be found,
    return None."""

    dates = [datetime.strptime(fixture.date + fixture.time, '%Y-%m-%d%H:%M')
             for fixture in fixtures]
    nearest = min(dates, key=lambda x: abs(x - selected_date))

    for fixture in fixtures:
        if nearest == datetime.strptime(fixture.date + fixture.time, '%Y-%m-%d%H:%M'):
            return fixture

    return None
