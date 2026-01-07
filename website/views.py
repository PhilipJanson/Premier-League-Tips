"""Views."""

from datetime import datetime
from flask import Blueprint, Response, flash, render_template, jsonify, abort, request
from flask_login import login_required, current_user
from .models import User, Tip, Fixture, FixtureStatus, Team, TeamStanding, General, Season
from .utils import (
    get_week_dates,
    get_fixture_tip_data,
    calculate_next_fixture,
    get_result_dict,
)
from . import db

views = Blueprint('views', __name__)
current_user: User

@views.route('/')
def endpoint_home() -> str:
    """Home page for the website."""

    start, end = get_week_dates()
    fixtures = Fixture.by_dates(General.get_active_season().season, start, end)
    context = {
        'fixtures': fixtures
    }
    return render_template('index.html', **context)

@views.route('/tip/<response>')
@login_required
def endpoint_tip(response: str) -> str:
    """Page to display upcoming fixtures and allow users to register new tips."""

    if response == 'register':
        flash("Tippning regristrerad")

    fixtures = Fixture.by_season(General.get_active_season().season)
    general = General.get()
    allow_late_modification = general.allow_late_modification if general else False
    fixture_data = get_fixture_tip_data(current_user, fixtures, allow_late_modification)
    next_fixture = calculate_next_fixture(fixtures, datetime.now())
    context = {
        'fixture_data': fixture_data,
        'next_fixture': next_fixture,
        'allow_late_modification': allow_late_modification
    }
    return render_template('tip.html', **context)

@views.route('/fixtures')
@login_required
def endpoint_fixtures() -> str:
    """Page to dislay all fixtures for the current season and view other user's tips."""

    fixtures = Fixture.by_season(General.get_active_season().season)
    context = {
        'all_users': User.all(),
        'fixtures': fixtures,
        'next_fixture': calculate_next_fixture(fixtures, datetime.now()),
        'tip_ids': [tip.fixture_id for tip in current_user.tips]
    }
    return render_template('fixtures.html', **context)

@views.route('/standings/<season>')
@login_required
def endpoint_standings(season: str) -> str:
    """Page to display all teams in a given season ordered by their rank."""

    standings = TeamStanding.by_season(season)
    last_update = standings[0].last_update if standings else None
    context = {
        'selected_season': season,
        'team_standings': standings,
        'last_update': last_update
    }
    return render_template('standings.html', **context)

@views.route('/stats/<season>')
@login_required
def endpoint_stats(season: str) -> str:
    """Page to display statistics for all users."""

    fixtures = (db.session.query(Fixture)
                          .join(Fixture.season)
                          .filter(Season.season == season)
                          .filter(Fixture.status == FixtureStatus.TIMED)
                          .all())
    user_result = get_result_dict(current_user.id, season)

    compare_result = {}
    compare_to_user = request.args.get('compareTo', type=str)
    if compare_to_user:
        compare_result = get_result_dict(compare_to_user, season)

    context = {
        'selected_season': season,
        'all_users': User.all(),
        'fixtures': fixtures,
        'user_result': user_result,
        'compare_result': compare_result
    }
    return render_template('stats.html', **context)

@views.route('/team-ranker')
@login_required
def endpoint_team_ranker() -> str:
    """Work in progress page to rank the teams."""

    context = {
        'teams': Team.by_season(General.get_active_season().season)
    }
    return render_template('teamranker.html', **context)

@views.route('/register-tips', methods=['POST'])
@login_required
def endpoint_register_tips() -> Response:
    """Endpoint for registering a new tip for the current user."""

    if not request.is_json:
        abort(415)
    data = request.get_json()

    if not isinstance(data, list):
        abort(400)

    try:
        for tip in data:
            if not isinstance(tip, dict):
                abort(400)

            try:
                fixture_id = int(tip.get('fixtureId'))
                value = str(tip.get('value')).strip()
            except (TypeError, ValueError):
                abort(400)

            if value not in {'1', 'X', '2'}:
                abort(400)

            fixture = Fixture.by_id(fixture_id)
            if not fixture:
                abort(404)

            Tip.create_or_update(current_user, fixture_id, value)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500)

    return jsonify({}), 200

@views.route('/privacy-policy')
def endpoint_privacy_policy() -> str:
    """Privacy policy."""

    return render_template('privacy_policy.html')
