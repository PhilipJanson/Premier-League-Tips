"""Schemas for serializing and deserializing API data using Marshmallow."""

from typing import Any
from marshmallow import Schema, fields, post_load, EXCLUDE
from marshmallow.utils import get_value, set_value
from .models import Fixture
from . import ACTIVE_SEASON

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
    def make_fixture(self, data: Any, **_kwargs) -> Fixture:
        fixture_round = int(data['fixture_round'].split(' - ')[1])
        fixture = Fixture(season=self.context.get("season", ACTIVE_SEASON),
                          round=fixture_round,
                          **data['fixture'],
                          **data['teams'],
                          **data['goals'])
        return fixture

    class Meta:
        unknown = EXCLUDE

