"""Utils."""

import json
import re
import requests

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any
from sqlalchemy import func, or_, case
from .models import Fixture, User, Result, Tip, Season, Team, MAX_USERNAME_LEN, MAX_PASSWORD_LEN
from . import db, LEAGUE_ID, api_secret_key

USERNAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{2,' + str(MAX_USERNAME_LEN - 1) + r'}$')
API_URL = 'https://v3.football.api-sports.io/'
# Dump API response data to console for debugging
DUMP_DATA = False

class ValidationError(Exception):
    """Raised when user input fails validation."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

def check_username_rules(username: str) -> None:
    """Check username rules. Raises ValidationError on fail."""
    if username is None or not USERNAME_REGEX.match(username):
        raise ValidationError("Ogiltigt användarnamn. Endast bokstäver, siffror, '-' och '_' är "
                              "tillåtet.")

def check_password_rules(password: str) -> None:
    """Check password rules. Raises ValidationError on fail."""

    if password is None or len(password) < 10:
        raise ValidationError("Lösenordet måste vara minst 10 tecken.")
    if len(password) > MAX_PASSWORD_LEN:
        raise ValidationError(f"Lösenordet får inte vara längre än {MAX_PASSWORD_LEN} tecken.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Lösenordet måste innehålla minst en stor bokstav.")
    if not re.search(r"[^\w\s]", password):
        raise ValidationError("Lösenordet måste innehålla minst ett specialtecken.")

# TODO: Change return types to datetime
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

    url = f"{API_URL}/{endpoint}?season={season.season}&league={LEAGUE_ID}"

    if endpoint == 'fixtures':
        url += '&timezone=Europe/Stockholm'

    headers = {
        'x-rapidapi-key': api_secret_key,
        'x-rapidapi-host': API_URL
    }

    response = requests.request('GET', url, headers=headers)
    response_json = response.json()
    if DUMP_DATA:
        print(json.dumps(response_json, indent=4))

    if response_json.get('errors', None):
        raise Exception("Failed to make API call: {}".format(response_json['errors']))

    return dict(response.headers), response_json

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

            if is_tip_correct(fixture, tip):
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

def is_tip_correct(fixture: Fixture, tip: Tip) -> bool:
    """Return True if the tip is correct, False otherwise."""

    score = fixture.home_score - fixture.away_score
    return (score > 0 and tip.tip == '1') or \
           (score < 0 and tip.tip == '2') or \
           (score == 0 and tip.tip == 'X')

def get_fixture_tip_data(user: User,
                         fixtures: list[Fixture],
                         allow_late_modification: bool) -> list[dict[str, Any]]:
    """Return a list with fixture data from a given user and list of fixtures. The fixture data will
       be a dict with the following format:
       ```
       {'fixture': <Fixture>, 'buttons': {'tip_value': <html_class>}, 'enabled': <bool>}
       ```
    """
    fixture_data: list[dict[str, Any]] = []
    # Mapped dict for getting tip value from a fixture_id
    mapped_tips: dict[int, str] = {tip.fixture_id: tip.tip for tip in user.tips}

    for fixture in fixtures:
        tip_value = mapped_tips.get(fixture.fixture_id)
        buttons = {
            '1': 'btn-outline-success',
            'X': 'btn-outline-success',
            '2': 'btn-outline-success'
        }
        enabled = False

        if fixture.status == "FT" and not allow_late_modification:
            if tip_value:
                buttons[tip_value] = "btn-success"
            buttons = {k: f"{v} disabled" for k, v in buttons.items()}
        elif fixture.status == "PST" and not allow_late_modification:
            buttons = {k: "btn-outline-warning disabled" for k in buttons}
        else:
            if tip_value:
                buttons[tip_value] = "btn-outline-success active"
            enabled = True

        fixture_data.append({
            'fixture': fixture,
            'buttons': buttons,
            'enabled': enabled
        })
    return fixture_data

def get_result_dict(user_id: str, season: str) -> dict[str, Any]:
    """Return the result object of the given user and season."""
    user = User.by_id(user_id)

    if not user or not season:
        return {}

    result = next((result for result in user.results if result.season.season == season), None)
    if not result:
        return {}

    round_stats = result.round_stats if (result.round_stats and result.round_stats.strip()) else {}
    team_stats = get_user_team_tip_distribution(user_id, season)

    return {
        'user': result.user,
        'result': {
            'total': int(result.total or 0),
            'finished': int(result.finished or 0),
            'correct': int(result.correct or 0),
            'incorrect': int(result.incorrect or 0),
            'tip_1': int(result.tip_1 or 0),
            'tip_X': int(result.tip_X or 0),
            'tip_2': int(result.tip_2 or 0),
            'round_stats': round_stats,
            'team_stats': team_stats
        }
    }

def get_user_team_tip_distribution(user_id: str, season: str) -> dict[str, Any]:
    """Returns tip counts and percentages for all teams in a given season for a specific user."""

    team_counts = (
        db.session.query(
            Team.team_id,
            Team.name,
            Team.logo,
            Tip.tip,
            func.count(Tip.id).label("tip_count"),
            func.sum(case((Tip.correct == 1, 1), else_=0)).label("correct_count")
        )
        .join(Fixture, or_(Fixture.home_team_id == Team.team_id,
                           Fixture.away_team_id == Team.team_id))
        .join(Tip, Tip.fixture_id == Fixture.fixture_id)
        .join(Season, Fixture.season_id == Season.id)
        .filter(Season.season == season)
        .filter(Tip.user_id == user_id)
        .group_by(Team.team_id, Team.name, Team.logo, Tip.tip)
        .order_by(Team.name)
        .all()
    )

    result = {}
    for team_id, team_name, logo, tip, tip_count, correct_count in team_counts:
        if team_id not in result:
            result[team_id] = {
                'team_name': team_name,
                'team_logo': logo,
                'counts': {'1': 0, 'X': 0, '2': 0},
                'percentages': {'1': 0, 'X': 0, '2': 0},
                'correct': 0,
                'incorrect': 0,
                'correct_percentage': 0,
            }
        result[team_id]['counts'][tip] = tip_count
        result[team_id]['correct'] += correct_count

    for team_id, data in result.items():
        total_tips = sum(data['counts'].values())
        if total_tips > 0:
            data['percentages'] = {k: (v / total_tips) * 100 for k, v in data['counts'].items()}
            data['correct_percentage'] = (data['correct'] / total_tips) * 100

    return result
