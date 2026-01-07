"""API Handler."""

import datetime
import json
import requests

from marshmallow import Schema, fields, post_load, EXCLUDE
from marshmallow.utils import get_value, set_value
from typing import Any
from .models import Fixture, FixtureStatus, Season, Team, TeamStanding
from . import api_secret_key

API_URI = 'api.football-data.org/v4'
# Dump API response data to console for debugging
DUMP_DATA = False

def api_call(endpoint: str, search_query: dict[str, str]) -> tuple[dict, Any]:
    headers = {
        'X-Auth-Token': api_secret_key
    }

    uri = f'https://{API_URI}{endpoint}'
    if search_query:
        query = '&'.join(f'{k}={v}' for k, v in search_query.items())
        uri = f'{uri}?{query}'

    response = requests.get(uri.strip(), headers=headers)
    response.raise_for_status()

    response_json = response.json()
    if DUMP_DATA:
        print(json.dumps(response_json, indent=4))

    if response_json.get('errors', None):
        raise Exception("Failed to make API call: {}".format(response_json['errors']))

    return dict(response.headers), response.json()

class Reach(fields.Field):
    """Field that can reach into nested dictionaries to get or set a value."""

    def __init__(self, inner: fields.Field, path: str, **kwargs):
        super().__init__(**kwargs)
        self.inner: fields.Field = inner
        self.path: str = path

    def _deserialize(self, value: Any, _attr: str, _data: Any, **kwargs):
        """Deserialize by reaching into a nested dictionary."""

        val = get_value(value, self.path)
        return self.inner.deserialize(val, **kwargs)

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        """Serialize by placing the value into a nested dictionary."""

        val = self.inner._serialize(value, attr, obj, **kwargs)
        ret = {}
        set_value(ret, self.path, val)
        return ret

class ScoreSchema(Schema):
    home_score = fields.Int(data_key='home', allow_none=True)
    away_score = fields.Int(data_key='away', allow_none=True)

class FixtureSchema(Schema):
    fixture_id = fields.Int(data_key='id')
    round = fields.Int(data_key='matchday')
    date_time = fields.DateTime(data_key='utcDate')
    status = fields.Enum(FixtureStatus)
    home_team_id = Reach(fields.Int(), data_key='homeTeam', path='id')
    away_team_id = Reach(fields.Int(), data_key='awayTeam', path='id')
    score = Reach(fields.Nested(ScoreSchema), data_key='score', path='fullTime')

    @post_load
    def make_fixture(self, data: dict[str, Any], **_kwargs) -> Fixture:
        season: Season = self.context.get('season')
        score_data = data.pop('score')
        return Fixture(season_id=season.id, **data, **score_data)

    class Meta:
        unknown = EXCLUDE

class TeamSchema(Schema):
    team_id = fields.Int(data_key='id')
    name = fields.Str()
    logo = fields.Str(data_key='crest')
    short_name = fields.Str(data_key='shortName')
    tla = fields.Str()

class StandingSchema(Schema):
    rank = fields.Int(data_key='position')
    points = fields.Int(allow_none=True)
    games_played = fields.Int(data_key='playedGames', allow_none=True)
    wins = fields.Int(data_key='won')
    draws = fields.Int(data_key='draw')
    losses = fields.Int(data_key='lost')
    goals_scored = fields.Int(data_key='goalsFor')
    goals_conceded = fields.Int(data_key='goalsAgainst')
    form = fields.Str(allow_none=True)
    team = fields.Nested(TeamSchema)

    @post_load
    def make_team_standing(self, data: dict[str, Any], **_kwargs) -> tuple[Team, TeamStanding]:
        season: Season = self.context.get('season')

        team_data = data.pop('team')
        team = Team(**team_data)

        # Not implemeted
        promotion = None
        status = 'same'

        # Parse form string from 'W,L,W,W,D' to 'WLWWD'
        form: str = data.pop('form', None)
        if form:
            form = form.replace(',', '')

        last_update = datetime.datetime.now()
        team_standing = TeamStanding(season_id=season.id,
                                     team_id=team.team_id,
                                     form=form,
                                     status=status,
                                     promotion=promotion,
                                     last_update=last_update,
                                     **data)
        return team, team_standing

    class Meta:
        unknown = EXCLUDE
