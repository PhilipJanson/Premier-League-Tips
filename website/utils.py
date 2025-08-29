"""Utils."""

import json
import requests

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any
from keys import API_KEY
from .models import Fixture, User, Result, Tip, Season
from . import LEAGUE_ID

URL = 'https://v3.football.api-sports.io/'
# Dump API response data to console for debugging
DUMP_DATA = False

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

def api_call(endpoint: str, season: Season) -> tuple[dict, Any]:
    """Fetch data from the API and return a tuple containing the response headers and data as
    json objects."""

    url = f"{URL}/{endpoint}?season={season.season}&league={LEAGUE_ID}"

    if endpoint == 'fixtures':
        url += '&timezone=Europe/Stockholm'

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': URL
    }

    response = requests.request('GET', url, headers=headers)
    if DUMP_DATA:
        print(json.dumps(response.json(), indent=4))
    return dict(response.headers), response.json()


def calculate_user_result(user: User, season: Season) -> Result:
    """Calculate the result for a user in a given season. Return a Result object."""

    # TODO: Impement team ranking score calculation
    if user is None:
        return None

    round_stats = defaultdict(lambda: {"tips": 0, "correct": 0})
    result = Result(user_id=user.id,
                    season_id=season.id,
                    total=0,
                    finished=0,
                    correct=0,
                    incorrect=0,
                    tip_1=0,
                    tip_X=0,
                    tip_2=0)

    for tip in user.tips:
        fixture = Fixture.by_id(tip.fixture_id)
        if fixture is None:
            continue

        # Calulate tip results
        result.total += 1
        if fixture.status == 'FT':
            result.finished += 1

            if is_correct(fixture, tip):
                result.correct += 1
                tip.correct = 1
            else:
                result.incorrect += 1
                tip.correct = -1

            if tip.tip == '1':
                result.tip_1 += 1
            elif tip.tip == 'X':
                result.tip_X += 1
            elif tip.tip == '2':
                result.tip_2 += 1

        # Calculate round stats
        stats = round_stats[fixture.round]
        stats["tips"] += 1
        if tip.correct == 1:
            stats["correct"] += 1
        result.round_stats = json.dumps(round_stats)

    result.last_update = datetime.now()
    return result

def is_correct(fixture: Fixture, tip: Tip) -> bool:
    """Return True if the tip is correct, False otherwise."""

    score = fixture.home_score - fixture.away_score
    return (score > 0 and tip.tip == '1') or \
           (score < 0 and tip.tip == '2') or \
           (score == 0 and tip.tip == 'X')
