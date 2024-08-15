from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean)
    tips = db.relationship('Tip')
    result = db.relationship('Result')

    @staticmethod
    def create(username, password):
        new_user = User(username=username, password=password,
                        is_admin=(username == "admin"))
        db.session.add(new_user)
        db.session.commit()

        return new_user

class Fixture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer)
    season = db.Column(db.String(4))
    round = db.Column(db.Integer)
    date = db.Column(db.String(10))
    time = db.Column(db.String(10))
    status = db.Column(db.String(10))
    home_team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    away_team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    home_team = db.relationship("Team", foreign_keys=[home_team_id])
    away_team = db.relationship("Team", foreign_keys=[away_team_id])
    home_score = db.Column(db.String(3))
    away_score = db.Column(db.String(3))

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(4))
    name = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    rank = db.Column(db.Integer)
    points = db.Column(db.Integer)
    games_played = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    draws = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    goals_scored = db.Column(db.Integer)
    goals_conceded = db.Column(db.Integer)
    form = db.Column(db.String(5))

class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer)
    tip = db.Column(db.String(1))
    correct = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(4))

    # Tip
    total = db.Column(db.Integer)
    finished = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    incorrect = db.Column(db.Integer)
    tip_1 = db.Column(db.Integer)
    tip_X = db.Column(db.Integer)
    tip_2 = db.Column(db.Integer)
    round_scores = db.Column(db.String(500))
    round_guesses = db.Column(db.String(500))

    # Placements
    placements = db.Column(db.String(500))
    placements_total = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class General(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(4))
    last_update = db.Column(db.String(40))
    remaining_requests = db.Column(db.Integer)
