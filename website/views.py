"""Views."""

import json

from datetime import datetime
from flask import Blueprint, Response, flash, render_template, jsonify, request
from flask_login import login_required, current_user
from .models import User, Tip, Fixture, Team, TeamStanding, Result, General, Season
from .utils import get_week_dates, calculate_next_fixture
from . import db

views = Blueprint('views', __name__)
current_user: User

@views.route('/')
def endpoint_home() -> str:
    """Home page for the website."""

    season_data = Season.get_season_data()
    start, end = get_week_dates()
    fixtures = Fixture.by_dates(season_data['active_season'].season, start, end)
    kwargs = {
        'season_data': season_data,
        'user': current_user,
        'fixtures': fixtures
    }
    return render_template('index.html', **kwargs)

@views.route('/tip/<response>')
@login_required
def endpoint_tip(response: str) -> str:
    """Page to display upcoming fixtures and allow users to register new tips."""

    if response == 'register':
        flash("Tippning regristrerad")

    season_data = Season.get_season_data()
    fixtures = Fixture.by_season(season_data['active_season'].season)
    general = General.get()
    allow_late_modification = general.allow_late_modification if general else False
    kwargs = {
        'season_data': season_data,
        'user': current_user,
        'fixtures': fixtures,
        'next_fixture': calculate_next_fixture(fixtures, datetime.now()),
        'allow_late_modification': allow_late_modification
    }
    return render_template('tip.html', **kwargs)

@views.route('/fixtures')
@login_required
def endpoint_fixtures() -> str:
    """Page to dislay all fixtures for the current season and view other user's tips."""

    season_data = Season.get_season_data()
    fixtures = Fixture.by_season(season_data['active_season'].season)
    kwargs = {
        'season_data': season_data,
        'user': current_user,
        'all_users': User.all(),
        'fixtures': fixtures,
        'next_fixture': calculate_next_fixture(fixtures, datetime.now()),
        'tip_ids': [tip.fixture_id for tip in current_user.tips]
    }
    return render_template('fixtures.html', **kwargs)

@views.route('/standings/<season>')
@login_required
def endpoint_standings(season: str) -> str:
    """Page to display all teams in a given season ordered by their rank."""

    kwargs = {
        'season_data': Season.get_season_data(),
        'selected_season': season,
        'user': current_user,
        'team_standings': TeamStanding.by_season(season)
    }
    return render_template('standings.html', **kwargs)

@views.route('/stats/<season>')
@login_required
def endpoint_stats(season: str) -> str:
    """Page to display statistics for all users."""

    fixtures = (db.session.query(Fixture)
                          .join(Fixture.season)
                          .filter(Season.season == season)
                          .filter(Fixture.status == 'NS')
                          .all())
    kwargs = {
        'season_data': Season.get_season_data(),
        'selected_season': season,
        'user': current_user,
        'all_users': User.all(),
        'fixtures': fixtures,
        'results': Result.by_season(season)
    }
    return render_template('stats.html', **kwargs)

@views.route('/tips', methods=['GET', 'POST'])
@login_required
def endpoint_tips() -> str:
    """Page to display all tips in a season for a specific user."""

    display_user = current_user

    if request.method == 'POST':
        username = request.form['form-username']
        display_user = User.by_username(username)

    season_data = Season.get_season_data()
    kwargs = {
        'season_data': season_data,
        'user': current_user,
        'all_users': User.all(),
        'display_user': display_user,
        'fixtures': Fixture.by_season(season_data['active_season'].season)
    }
    return render_template('tips.html', **kwargs)

@views.route('/team-ranker')
@login_required
def endpoint_team_ranker() -> str:
    """Work in progress page to rank the teams."""

    season_data = Season.get_season_data()
    kwargs = {
        'season_data': season_data,
        'user': current_user,
        'teams': Team.by_season(season_data['active_season'].season)
    }
    return render_template('teamranker.html', **kwargs)

@views.route('/register-tips', methods=['POST'])
def endpoint_register_tips() -> Response:
    """Endpoint for registering a new tip for the current user."""

    tips = json.loads(request.data)

    for tip in tips:
        fixture_id = int(str(tip['fixtureId']).strip())
        value = str(tip['value']).strip()
        Tip.create_or_update(current_user, fixture_id, value)
    db.session.commit()

    return jsonify({})
