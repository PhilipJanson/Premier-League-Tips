"""Schemas for serializing and deserializing API data using Marshmallow."""

import datetime

from typing import Any
from marshmallow import Schema, fields, post_load, EXCLUDE
from marshmallow.utils import get_value, set_value
from .models import Fixture, Team, TeamStanding, Season

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

class FixtureNestedSchema(Schema):
    fixture_id = fields.Int(data_key='id')
    date_time = fields.DateTime(data_key='date')
    status = Reach(fields.Str(), data_key='status', path='short')

    class Meta:
        unknown = EXCLUDE

class FixtureTeamsSchema(Schema):
    home_team_id = Reach(fields.Int(), data_key='home', path='id')
    away_team_id = Reach(fields.Int(), data_key='away', path='id')

class FixtureGoalsSchema(Schema):
    home_score = fields.Int(data_key='home', allow_none=True)
    away_score = fields.Int(data_key='away', allow_none=True)

class FixtureSchema(Schema):
    fixture = fields.Nested(FixtureNestedSchema)
    teams = fields.Nested(FixtureTeamsSchema)
    goals = fields.Nested(FixtureGoalsSchema)
    fixture_round = Reach(fields.Str(), data_key='league', path='round')

    @post_load
    def make_fixture(self, data: dict[str, Any], **_kwargs) -> Fixture:
        season: Season = self.context.get("season")
        fixture_round = int(data['fixture_round'].split(' - ')[1])
        fixture = Fixture(season_id=season.id,
                          round=fixture_round,
                          **data['fixture'],
                          **data['teams'],
                          **data['goals'])
        return fixture

    class Meta:
        unknown = EXCLUDE

class TeamNestedSchema(Schema):
    team_id = fields.Int(data_key='id')
    name = fields.Str()
    logo = fields.Str()

class TeamGoalsSchema(Schema):
    goals_scored = fields.Int(data_key='for')
    goals_conceded = fields.Int(data_key='against')

class TeamAllSchema(Schema):
    games_played = fields.Int(data_key='played')
    wins = fields.Int(data_key='win')
    draws = fields.Int(data_key='draw')
    losses = fields.Int(data_key='lose')
    goals = fields.Nested(TeamGoalsSchema)

    class Meta:
        unknown = EXCLUDE

class TeamSchema(Schema):
    team = fields.Nested(TeamNestedSchema)
    all = fields.Nested(TeamAllSchema)
    rank = fields.Int()
    points = fields.Int(allow_none=True)
    form = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)

    @post_load
    def make_team(self, data: dict[str, Any], **_kwargs) -> tuple[Team, TeamStanding]:
        team = Team(**data['team'])

        season: Season = self.context.get("season")
        last_update = datetime.datetime.now()

        # Deserialize promotion from description
        promotion = data.get('description', None)
        if promotion:
            if "Champions League" in promotion:
                promotion = 'CL'
            elif "Europa League" in promotion:
                promotion = 'EL'
            elif "Conference League" in promotion:
                promotion = 'ECL'
            elif "Relegation" in promotion:
                promotion = 'R'

        # Extract goals scored and conceded from nested 'all' dictionary
        goals = data['all'].pop('goals')
        goals_scored = goals.get('goals_scored', 0)
        goals_conceded = goals.get('goals_conceded', 0)

        standing = TeamStanding(season_id=season.id,
                                rank=data['rank'],
                                points=data.get('points', 0),
                                goals_scored=goals_scored,
                                goals_conceded=goals_conceded,
                                form=data.get('form', ''),
                                status=data.get('status', ''),
                                promotion=promotion,
                                last_update=last_update,
                                team_id=team.team_id,
                                **data['all'])
        return team, standing

    class Meta:
        unknown = EXCLUDE
