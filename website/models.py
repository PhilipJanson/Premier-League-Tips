"""Models."""

from __future__ import annotations

import uuid

from typing import Any
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload
from . import db, ACTIVE_SEASON

class Updateable:
    """Mixin class to add update_attributes method to models."""

    def update_attributes(self, data: dict) -> None:
        """Update the attributes of the instance with the given data dictionary."""

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class User(db.Model, UserMixin):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(500))
    is_admin: Mapped[bool] = mapped_column(Boolean)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    tips: Mapped[list['Tip']] = relationship(back_populates='user')
    results: Mapped[list['Result']] = relationship(back_populates='user')
    favorite_team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'), nullable=True)
    favorite_team: Mapped['Team'] = relationship("Team", foreign_keys=[favorite_team_id])

    @staticmethod
    def create(username: str, password: str) -> User:
        """Create a new user with a username and a password and add it to the database. Return the
        created user."""

        user = User(username=username, password=password, is_admin=username == 'admin')
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def all() -> list[User]:
        """Return the list of all users."""

        return db.session.execute(db.select(User)).scalars().all()

    @staticmethod
    def by_username(username: str) -> User:
        """Return a user given a username."""

        return db.session.execute(db.select(User).filter_by(username=username)).scalar()

class Fixture(db.Model, Updateable):
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[str] = mapped_column(String(4))
    round: Mapped[int] = mapped_column(Integer)
    date_time: Mapped[DateTime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(10))
    home_team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'))
    away_team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'))
    home_team: Mapped['Team'] = relationship("Team", foreign_keys=[home_team_id])
    away_team: Mapped['Team'] = relationship("Team", foreign_keys=[away_team_id])
    home_score: Mapped[int] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int] = mapped_column(Integer, nullable=True)

    @staticmethod
    def by_id(fixture_id: int) -> Fixture:
        """Return the fixture given an ID."""

        return db.session.execute(db.select(Fixture).filter_by(fixture_id=fixture_id)).scalar()

    @staticmethod
    def by_season(season: str) -> list[Fixture]:
        """Return the list of fixtures in a given season."""

        return db.session.execute(db.select(Fixture).filter_by(season=season)).scalars().all()

    @staticmethod
    def by_dates(season: str, start_date: str, end_date: str) -> list[Fixture]:
        """Return the list of fixtures in a given season between two dates."""

        # TODO: check if I should use select or query
        return db.session.execute(db.select(Fixture)
                                  .filter_by(season=season)
                                  .filter(Fixture.date_time >= start_date)
                                  .filter(Fixture.date_time <= end_date)).scalars().all()

    @staticmethod
    def create_or_update(fixture: Fixture) -> None:
        """Create or update a fixture and commit it to the database."""

        existing_fixture = Fixture.by_id(fixture.fixture_id)
        if existing_fixture is not None:
            existing_fixture.update_attributes(fixture.__dict__)
        else:
            db.session.add(fixture)
        db.session.commit()

class Team(db.Model, Updateable):
    team_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    logo: Mapped[str] = mapped_column(String(200))
    standings: Mapped[list['TeamStanding']] = relationship("TeamStanding", back_populates='team')

    @staticmethod
    def by_rank(season: str) -> list[Team]:
        """Return the list of teams in a given season ordered by their rank."""

        return (db.session.query(Team)
                .join(Team.standings)
                .filter(TeamStanding.season == season)
                .order_by(TeamStanding.rank)
                .options(joinedload(Team.standings))
                .all())

    @staticmethod
    def by_name(season: str) -> list[Team]:
        """Return the list of teams in a given season ordered by their name."""

        return (db.session.query(Team)
                .join(Team.standings)
                .filter(TeamStanding.season == season)
                .order_by(Team.name)
                .options(joinedload(Team.standings))
                .all())

    # TODO: handle the standings
    @staticmethod
    def create_or_update(team: Team) -> None:
        """Create or update a team and commit it to the database."""

        existing_team = Fixture.by_id(team.team_id)
        if existing_team is not None:
            existing_team.update_attributes(team.__dict__)
        else:
            db.session.add(team)
        db.session.commit()

    @staticmethod
    def parse_json(standings_response: Any, season: str) -> None:
        """"""

        for team_json in standings_response['response'][0]['league']['standings']:
            team_obj = team_json['team']
            all_obj = team_json['all']
            team_id = team_obj['id']

            team_data = {
                'team_id': team_id,
                'name': team_obj['name'],
                'logo': team_obj['logo'],
            }

            standings_data = {
                'season': season,
                'rank': team_json['rank'],
                'points': team_json['points'],
                'games_played': all_obj['played'],
                'wins': all_obj['win'],
                'draws': all_obj['draw'],
                'losses': all_obj['lose'],
                'goals_scored': all_obj['goals']['for'],
                'goals_conceded': all_obj['goals']['against'],
                'form': team_json['form'],
                'team_id': team_id
            }

            print(f"Parsing team ID {team_id}")
            team = Team.by_id(team_id)

            if not team:
                team = Team(season=season, **team_data)
                db.session.add(team)
            else:
                team.update_attributes(team_data)

class TeamStanding(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))
    rank: Mapped[int] = mapped_column(Integer, nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=True)
    games_played: Mapped[int] = mapped_column(Integer, nullable=True)
    wins: Mapped[int] = mapped_column(Integer, nullable=True)
    draws: Mapped[int] = mapped_column(Integer, nullable=True)
    losses: Mapped[int] = mapped_column(Integer, nullable=True)
    goals_scored: Mapped[int] = mapped_column(Integer, nullable=True)
    goals_conceded: Mapped[int] = mapped_column(Integer, nullable=True)
    form: Mapped[str] = mapped_column(String(5), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('team.team_id'))
    team: Mapped['Team'] = relationship(back_populates='standings')

class Tip(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer)
    tip: Mapped[str] = mapped_column(String(1))
    correct: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='tips')

    @staticmethod
    def by_fixure_id(user: User, fixture_id: int) -> Tip:
        """Return the tip in a given a user and a fixture ID."""

        return db.session.execute(db.select(Tip)
                                  .filter_by(user_id=user.id)
                                  .filter_by(fixture_id=fixture_id)).scalar()

class Result(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))

    # Tip
    total: Mapped[int] = mapped_column(Integer)
    finished: Mapped[int] = mapped_column(Integer)
    correct: Mapped[int] = mapped_column(Integer)
    incorrect: Mapped[int] = mapped_column(Integer)
    tip_1: Mapped[int] = mapped_column(Integer)
    tip_X: Mapped[int] = mapped_column(Integer)
    tip_2: Mapped[int] = mapped_column(Integer)
    round_scores: Mapped[str] = mapped_column(String(500))
    round_guesses: Mapped[str] = mapped_column(String(500))

    # Placements
    placements: Mapped[int] = mapped_column(String(500))
    placements_total: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='results')

    @staticmethod
    def by_season(season: str) -> list[Result]:
        """Return the list of results in a given season."""

        return db.session.execute(db.select(Result).filter_by(season=season)).scalars().all()

class General(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))
    last_update: Mapped[datetime] = mapped_column(DateTime)
    remaining_requests: Mapped[int] = mapped_column(Integer)

    @staticmethod
    def get() -> General:
        """Return the General instance."""

        return db.session.execute(db.select(General)).scalar()

    # TODO: the season should not be updated here, only last_update and remaining_requests
    # The season should be updated only when a new season starts and should be in a manual trigger
    @staticmethod
    def update(season: str, last_update: str, remaining_requests: int) -> None:
        """Update or create the General instance and commit it to the database."""

        general = General.get()
        if general:
            general.season = season
            general.last_update = last_update
            general.remaining_requests = remaining_requests
        else:
            general = General(season=season,
                              last_update=last_update,
                              remaining_requests=remaining_requests)
            db.session.add(general)
        db.session.commit()

    @staticmethod
    def get_active_season() -> str:
        """Return the current active season."""

        general = General.get()
        if general:
            return general.season
        return ACTIVE_SEASON
