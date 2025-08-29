"""Models."""

from __future__ import annotations

import uuid

from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload
from typing import Any
from . import db, ACTIVE_SEASON, SEASON_DISPLAY_NAME

class Updateable:
    """Mixin class to add update_attributes method to models."""

    def update_attributes(self, data: dict) -> None:
        """Update the attributes of the instance with the given data dictionary.
           Ignore None and private values.
        """
        for key, value in data.items():
            if not str(key).startswith('_') and hasattr(self, key) and value is not None:
                setattr(self, key, value)

class User(db.Model, UserMixin):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(500))
    is_admin: Mapped[bool] = mapped_column(Boolean)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                default=lambda: datetime.now(timezone.utc))
    tips: Mapped[list['Tip']] = relationship("Tip", back_populates='user')
    results: Mapped[list['Result']] = relationship("Result", back_populates='user')
    favorite_team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'), nullable=True)
    favorite_team: Mapped['Team'] = relationship("Team", foreign_keys=[favorite_team_id])

    @staticmethod
    def create(username: str, password: str) -> User:
        """Create a new user with a username and a password and add it to the database. Return the
        created user."""

        user = User(username=username, password=password, is_admin=username == 'admin')
        db.session.add(user)
        current_app.logger.debug(f"Created user: {user.username} ({user.id})")
        return user

    @staticmethod
    def all() -> list[User]:
        """Return the list of all users."""

        return db.session.execute(db.select(User)).scalars().all()

    @staticmethod
    def by_id(uuid: str) -> User:
        """Return the user given an ID."""

        return db.session.execute(db.select(User).filter_by(id=uuid)).scalar_one_or_none()

    @staticmethod
    def by_username(username: str) -> User:
        """Return a user given a username."""

        return db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

class Fixture(db.Model, Updateable):
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey('season.id'), nullable=False)
    season: Mapped['Season'] = relationship("Season", foreign_keys=[season_id])
    round: Mapped[int] = mapped_column(Integer, nullable=True)
    date_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    # Status of the fixture. 'FT': full time, 'NS': not started, 'PST': postponed.
    status: Mapped[str] = mapped_column(String(10), nullable=False, default='NS')
    home_team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'))
    away_team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'))
    home_team: Mapped['Team'] = relationship("Team", foreign_keys=[home_team_id])
    away_team: Mapped['Team'] = relationship("Team", foreign_keys=[away_team_id])
    home_score: Mapped[int] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int] = mapped_column(Integer, nullable=True)

    @staticmethod
    def by_id(fixture_id: int) -> Fixture:
        """Return the fixture given an ID."""

        return (db.session.execute(db.select(Fixture).filter_by(fixture_id=fixture_id))
                          .scalar_one_or_none())

    @staticmethod
    def by_season(season: str) -> list[Fixture]:
        """Return the list of fixtures in a given season."""

        return (db.session.query(Fixture)
                .join(Fixture.season)
                .filter(Season.season == season)
                .all())

    @staticmethod
    def by_dates(season: str, start_date: str, end_date: str) -> list[Fixture]:
        """Return the list of fixtures in a given season between two dates."""

        return (db.session.query(Fixture)
                .join(Fixture.season)
                .filter(Season.season == season)
                .filter(Fixture.date_time >= start_date)
                .filter(Fixture.date_time <= end_date)
                .all())

    @staticmethod
    def create_or_update(fixture: Fixture) -> None:
        """Create or update a fixture."""

        existing_fixture = Fixture.by_id(fixture.fixture_id)
        if existing_fixture is not None:
            existing_fixture.update_attributes(fixture.__dict__)
            current_app.logger.debug(f"Updated fixture: {fixture.fixture_id}")
        else:
            db.session.add(fixture)
            current_app.logger.debug(f"Added fixture: {fixture.fixture_id}")

class Team(db.Model, Updateable):
    team_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    logo: Mapped[str] = mapped_column(String(200), nullable=True, default=None)
    standings: Mapped[list['TeamStanding']] = relationship("TeamStanding", back_populates='team')

    @staticmethod
    def by_id(team_id: int) -> Team:
        """Return the fixture given an ID."""

        return db.session.execute(db.select(Team).filter_by(team_id=team_id)).scalar_one_or_none()

    @staticmethod
    def by_season(season: str) -> list[Team]:
        """Return the list of teams in a given season ordered by their name."""

        return (db.session.query(Team)
                .join(Team.standings)
                .join(TeamStanding.season)
                .filter(Season.season == season)
                .order_by(Team.name)
                .options(joinedload(Team.standings))
                .all())

    @staticmethod
    def create_or_update_team_and_standing(team: Team, standings: TeamStanding) -> None:
        """Create or update a team and its standing for a season."""

        # Check if team exists, else create it
        existing_team = Team.by_id(team.team_id)
        if existing_team is not None:
            existing_team.update_attributes(team.__dict__)
            current_app.logger.debug(f"Updated team: {team.name} ({team.team_id})")
        else:
            db.session.add(team)
            current_app.logger.debug(f"Added team: {team.name} ({team.team_id})")

        # Check if standings exists for this team and season
        exisiting_standings: TeamStanding = (db.session.execute(db.select(TeamStanding)
                                                       .filter_by(team_id=team.team_id,
                                                                  season=standings.season))
                                                       .scalar_one_or_none())
        if exisiting_standings is not None:
            print(exisiting_standings.goals_scored)
            print(standings.goals_scored)
            exisiting_standings.update_attributes(standings.__dict__)
            current_app.logger.debug(f"Updated standings for team: {team.name} "
                                     f"(ID: {team.team_id}, season: {standings.season})")
        else:
            db.session.add(standings)
            current_app.logger.debug(f"Added standings for team: {team.name} "
                                     f"(ID: {team.team_id}, season: {standings.season})")

class TeamStanding(db.Model, Updateable):
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey('season.id'), nullable=False)
    season: Mapped['Season'] = relationship("Season", foreign_keys=[season_id])
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    draws: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    goals_scored: Mapped[int] = mapped_column(Integer, default=0)
    goals_conceded: Mapped[int] = mapped_column(Integer, default=0)
    # Recent form of the team, e.g. "WWDLW", min leghth 0, max length 5
    form: Mapped[str] = mapped_column(String(5), default='')
    # Current status of the team in table. Always 'same'.
    status: Mapped[str] = mapped_column(String(20), default='')
    # Promotion status for a team. Valid values are 'CL', 'EL', 'ELC', 'R' or None.
    promotion: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    last_update: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'))
    team: Mapped['Team'] = relationship("Team", back_populates='standings')

    @staticmethod
    def by_season(season: str) -> list[TeamStanding]:
        """Return the list of teams in a given season ordered by their rank."""

        return (db.session.query(TeamStanding)
                .join(TeamStanding.season)
                .filter(Season.season == season)
                .order_by(TeamStanding.rank)
                .all())

class Tip(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer)
    # Valid values are '1', 'X' or '2'
    tip: Mapped[str] = mapped_column(String(1))
    # Status of the tip. 1: correct, -1: incorrect, 0: not yet decided
    correct: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship("User", back_populates='tips')

    @staticmethod
    def by_fixure_id(user: User, fixture_id: int) -> Tip:
        """Return the tip in a given a user and a fixture ID."""

        return db.session.execute(db.select(Tip)
                                  .filter_by(user_id=user.id)
                                  .filter_by(fixture_id=fixture_id)).scalar_one_or_none()

    @staticmethod
    def create_or_update(user: User, fixture_id: int, value: str) -> Tip:
        """Create or update a tip for a user and a fixture ID. Return the created or updated tip."""

        if value not in ['1', 'X', '2'] or user is None:
            return None

        tip = Tip.by_fixure_id(user, fixture_id)
        if tip is not None:
            tip.tip = value
        else:
            tip = Tip(fixture_id=fixture_id, tip=value, user_id=user.id)
            db.session.add(tip)

        return tip

# Association table to link Result and Team with an additional 'rank' column
result_team_association = Table(
    'result_team_association',
    db.metadata,
    Column('result_id', ForeignKey('result.id'), primary_key=True),
    Column('team_id', ForeignKey('team.team_id'), primary_key=True),
    Column('rank', Integer, nullable=False)
)

class Result(db.Model, Updateable):
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey('season.id'), nullable=False)
    season: Mapped['Season'] = relationship("Season", foreign_keys=[season_id])
    # Total tips made
    total: Mapped[int] = mapped_column(Integer, default=0)
    # Tips that have been decided
    finished: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    incorrect: Mapped[int] = mapped_column(Integer, default=0)
    tip_1: Mapped[int] = mapped_column(Integer, default=0)
    tip_X: Mapped[int] = mapped_column(Integer, default=0)
    tip_2: Mapped[int] = mapped_column(Integer, default=0)
    # Round stats stored as JSON string in the format:
    # {"<round>": {"tips": <value>, "correct": <value>}
    round_stats: Mapped[str] = mapped_column(Text, default='')
    # Teams ordered by the user's ranking
    team_rankings: Mapped[list['Team']] = relationship("Team",
                                                       secondary=result_team_association,
                                                       order_by=result_team_association.c.rank)
    # Total score for team rankings
    placements_total: Mapped[int] = mapped_column(Integer, default=0)
    last_update: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship("User", back_populates='results')

    @staticmethod
    def by_season(season: str) -> list[Result]:
        """Return the list of results in a given season."""

        return (db.session.query(Result)
                .join(Result.season)
                .filter(Season.season == season)
                .all())

    @staticmethod
    def create_or_update(result: Result) -> None:
        """Create or update a fixture."""

        existing_result = (db.session.query(Result)
                           .filter(Result.season_id == result.season_id,
                                   Result.user_id == result.user_id)
                           .one_or_none())
        if existing_result is not None:
            existing_result.update_attributes(result.__dict__)
            current_app.logger.debug(f"Updated result: {result.id}")
        else:
            db.session.add(result)
            current_app.logger.debug(f"Added result: {result.id}")

class General(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey('season.id'), nullable=False)
    season: Mapped['Season'] = relationship("Season", foreign_keys=[season_id])
    last_update: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    remaining_requests: Mapped[int] = mapped_column(Integer, nullable=True)
    allow_late_modification: Mapped[bool] = mapped_column(Boolean, default=False)

    @staticmethod
    def get() -> General:
        """Return the General instance."""

        return db.session.execute(db.select(General)).scalar_one_or_none()

    @staticmethod
    def create(season: Season) -> None:
        """Create the General instance and add it to the database."""

        if General.get() is None:
            general = General(season_id=season.id)
            db.session.add(general)

    @staticmethod
    def update(last_update: str, remaining_requests: int) -> None:
        """Update the General instance in the database."""

        general = General.get()
        if general is not None:
            general.last_update = last_update
            general.remaining_requests = remaining_requests

    @staticmethod
    def get_active_season() -> Season:
        """Return the current active season."""

        general = General.get()
        if general and general.season is not None:
            return general.season
        current_app.logger.warning("Active season not set in General table. "
                                   f"Using default: {ACTIVE_SEASON}")

        # Only used as a fallback if nothing is set. This object is not persisent.
        return Season(id=0, season=ACTIVE_SEASON, display_name=SEASON_DISPLAY_NAME)

class Season(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    @staticmethod
    def by_season(season: str) -> Season:
        """Return the matching season instance."""

        return db.session.execute(db.select(Season).filter_by(season=season)).scalar_one_or_none()

    @staticmethod
    def all() -> list[Season]:
        """Return the list of all seasons."""

        return db.session.execute(db.select(Season).order_by(Season.season)).scalars().all()

    @staticmethod
    def create(season: str) -> Season:
        """Create a new season and return it."""

        display_name = f"{season}-{str(int(season) + 1)[2:]}"
        new_season = Season(season=season, display_name=display_name)
        db.session.add(new_season)
        return new_season

    @staticmethod
    def get_season_data() -> dict[str, Any]:
        """Return a dictionary with the active season and all seasons."""

        return {
            'active_season': General.get_active_season(),
            'all_seasons': Season.all()
        }
