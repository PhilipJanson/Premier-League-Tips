"""Utils."""

import requests

from datetime import date, datetime, timedelta
from typing import Any
from keys import API_KEY
from .models import Fixture
from . import LEAGUE_ID

URL = 'https://v3.football.api-sports.io/'

def get_week_dates() -> tuple[str, str]:
    """Return the start and end dates in string format for the current week."""

    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return str(start), str(end)

def calculate_next_fixture(fixtures: list[Fixture], selected_date: datetime) -> Fixture:
    """Return the next upcoming fixture given a datetime object. If a fixture can't be found,
    return None."""

    dates = [fixture.date_time for fixture in fixtures]
    if not dates:
        return None

    nearest = min(dates, key=lambda x: abs(x - selected_date))
    for fixture in fixtures:
        if nearest == fixture.date_time:
            return fixture

    return None

def api_call(endpoint: str, season: str) -> tuple[dict, Any]:
    """Fetch data from the API and return a tuple containing the response headers and data as
    json objects."""

    url = f"{URL}/{endpoint}?season={season}&league={LEAGUE_ID}"

    if endpoint == 'fixtures':
        url += '&timezone=Europe/Stockholm'

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': URL
    }

    response = requests.request('GET', url, headers=headers)
    return dict(response.headers), response.json()
