"""Models."""

from __future__ import annotations
from flask_login import UserMixin
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db

class User(db.Model, UserMixin):
    """User."""    

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(500))
    is_admin: Mapped[bool] = mapped_column(Boolean)
    tips: Mapped[list['Tip']] = relationship(back_populates='user')
    #TODO: rename to results, since it holds one for each season
    result: Mapped[list['Result']] = relationship(back_populates='user')

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

class Fixture(db.Model):
    """Fixture."""    

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer)
    season: Mapped[str] = mapped_column(String(4))
    round: Mapped[int] = mapped_column(Integer)

    #TODO: change to datetime
    date: Mapped[str] = mapped_column(String(10))
    time: Mapped[str] = mapped_column(String(10))

    status: Mapped[str] = mapped_column(String(10))
    home_team_id: Mapped[int] = mapped_column(ForeignKey('team.id'))
    away_team_id: Mapped[int] = mapped_column(ForeignKey('team.id'))
    home_team: Mapped['Team'] = relationship("Team", foreign_keys=[home_team_id])
    away_team: Mapped['Team'] = relationship("Team", foreign_keys=[away_team_id])
    home_score = mapped_column(String(3))
    away_score = mapped_column(String(3))

    @staticmethod
    def by_season(season: str) -> list[Fixture]:
        """Return the list of fixtures in a given season."""

        return db.session.execute(db.select(Fixture).filter_by(season=season)).scalars().all()

    @staticmethod
    def by_dates(season: str, start_date: str, end_date: str) -> list[Fixture]:
        """Return the list of fixtures in a given season between two dates."""

        return db.session.execute(db.select(Fixture)
                                  .filter_by(season=season)
                                  .filter(Fixture.date >= start_date)
                                  .filter(Fixture.date <= end_date)).scalars().all()

class Team(db.Model):
    """Team."""    

    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))
    name: Mapped[str] = mapped_column(String(100))
    logo: Mapped[str] = mapped_column(String(200))
    rank: Mapped[int] = mapped_column(Integer)
    points: Mapped[int] = mapped_column(Integer)
    games_played: Mapped[int] = mapped_column(Integer)
    wins: Mapped[int] = mapped_column(Integer)
    draws: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)
    goals_scored: Mapped[int] = mapped_column(Integer)
    goals_conceded: Mapped[int] = mapped_column(Integer)
    form: Mapped[str] = mapped_column(String(5))

    @staticmethod
    def by_rank(season: str) -> list[Team]:
        """Return the list of teams in a given season ordered by their rank."""

        return db.session.execute(db.select(Team)
                                  .filter_by(season=season)
                                  .order_by(Team.rank)).scalars().all()

    @staticmethod
    def by_name(season: str) -> list[Team]:
        """Return the list of teams in a given season ordered by their name."""

        return db.session.execute(db.select(Team)
                                  .filter_by(season=season)
                                  .order_by(Team.name)).scalars().all()

class Tip(db.Model):
    """Tip."""    

    id: Mapped[int] = mapped_column(primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer)
    tip: Mapped[str] = mapped_column(String(1))
    correct: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='tips')

    @staticmethod
    def by_fixure_id(user: User, fixture_id: int) -> Tip:
        """Return the tip in a given a user and a fixture ID."""

        return db.session.execute(db.select(Tip)
                                  .filter_by(user_id=user.id)
                                  .filter_by(fixture_id=fixture_id)).scalar()

class Result(db.Model):
    """Result."""    

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
    
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='result')

    @staticmethod
    def by_season(season: str) -> list[Result]:
        """Return the list of results in a given season."""

        return db.session.execute(db.select(Result).filter_by(season=season)).scalars().all()

class General(db.Model):
    """General."""    

    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))

    #TODO: change to date time?
    last_update: Mapped[str] = mapped_column(String(40))
    remaining_requests: Mapped[int] = mapped_column(Integer)
