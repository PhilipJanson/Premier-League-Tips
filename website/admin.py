"""Admin."""

import datetime
import re
import time

from flask import (
    Blueprint,
    Response,
    abort,
    render_template,
    flash, redirect,
    jsonify,
    url_for,
    request,
    current_app
)
from flask_login import login_required, current_user
from functools import wraps
from typing import Any, Callable
from .api_handler import FixtureSchema, StandingSchema, api_call
from .models import User, General, Fixture, Team, Result, Season
from .utils import calculate_user_result
from . import db

admin = Blueprint('admin', __name__)
current_user: User

def admin_required(func) -> Callable:
    @wraps(func)
    def decorated(*args, **kwargs) -> Any:
        if not current_user.is_admin:
            flash("Admin privileges are needed to access this endpoint", category='error')

            if request.accept_mimetypes.best == 'application/json':
                abort(403)

            return redirect(url_for('views.endpoint_home'))

        return func(*args, **kwargs)
    return decorated

@admin.route('')
@login_required
@admin_required
def endpoint_admin() -> str:
    """Page to display options for an admin user."""

    context = {
        'all_users': User.all(),
    }
    return render_template('admin.html', **context)

@admin.route('/fetch-api-fixtures', methods=['POST'])
@login_required
@admin_required
def endpoint_fetch_api_fixtures() -> Response:
    """Fetch fixture data from the API and update the database."""

    if General.get() is None:
        flash("No general table exists.", category='error')
        abort(404)

    current_app.logger.debug("Starting task to fetch API fixture data...")
    season = General.get_active_season()
    start_time = time.perf_counter()

    try:
        headers, fixture_response = api_call('/competitions/PL/matches',
                                             {'season': season.season})
        schema = FixtureSchema(context={'season': season})
        _parse_headers(headers)

        for fixture_json in fixture_response['matches']:
            fixture = schema.load(fixture_json)
            Fixture.create_or_update(fixture)

        db.session.commit()
        end_time = time.perf_counter()
        status = f"Task finished in {(end_time - start_time):.2f} seconds."
        flash(status, category='success')
        current_app.logger.debug(status)
    except Exception as error:
        end_time = time.perf_counter()
        flash(f"Task failed in {(end_time - start_time):.2f} seconds: "
              f"{type(error).__name__}: {error}", category='error')
        current_app.logger.exception(error)

    return jsonify({}), 200

@admin.route('/fetch-api-standings', methods=['POST'])
@login_required
@admin_required
def endpoint_fetch_api_standings() -> Response:
    """Fetch standings data from the API and update the database."""

    if General.get() is None:
        flash("No general table exists.", category='error')
        return jsonify({}), 404

    current_app.logger.debug("Starting task to fetch API standings data...")
    season = General.get_active_season()
    start_time = time.perf_counter()

    try:
        headers, standings_response = api_call('/competitions/PL/standings',
                                               {'season': season.season})
        schema = StandingSchema(context={'season': season})
        _parse_headers(headers)

        for team_json in standings_response['standings'][0]['table']:
            team, standings = schema.load(team_json)
            Team.create_or_update_team_and_standing(team, standings)

        db.session.commit()
        end_time = time.perf_counter()
        status = f"Task finished in {(end_time - start_time):.2f} seconds."
        flash(status, category='success')
        current_app.logger.debug(status)
    except Exception as error:
        end_time = time.perf_counter()
        flash(f"Task failed in {(end_time - start_time):.2f} seconds: "
              f"{type(error).__name__}: {error}", category='error')
        current_app.logger.exception(error)

    return jsonify({}), 200

@admin.route('/calculate-results', methods=['POST'])
@login_required
@admin_required
def endpoint_calculate_results() -> Response:
    """Fetch standings data from the API and update the database."""

    if General.get() is None:
        flash("No general table exists.", category='error')
        return jsonify({}), 404

    current_app.logger.debug("Starting task to calculate results...")
    season = General.get_active_season()
    start_time = time.perf_counter()

    for user in User.all():
        result = calculate_user_result(user, season)
        Result.create_or_update(result)

    db.session.commit()
    end_time = time.perf_counter()
    status = f"Task finished in {(end_time - start_time):.2f} seconds."
    flash(status, category='success')
    current_app.logger.debug(status)

    return jsonify({}), 200

@admin.route('/add-season', methods=['POST'])
@login_required
@admin_required
def endpoint_add_season() -> Response:
    """Add a new season to the database."""

    if not request.is_json:
        abort(415)
    data = request.get_json()

    try:
        season = str(data.get('season')).strip()
    except (TypeError, ValueError):
        abort(400)

    if not re.fullmatch(r'^[12][0-9]{3}$', season):
        flash(f"Incorrect format for season: {season}", category='error')
        abort(404)

    new_season = Season.create(season)
    db.session.commit()
    flash(f"Season {new_season.display_name} created.", category='success')

    return jsonify({}), 200

@admin.route('/set-active-season', methods=['POST'])
@login_required
@admin_required
def endpoint_set_active_season() -> Response:
    """Add a new season to the database."""

    if not request.is_json:
        abort(415)
    data = request.get_json()

    try:
        season_string = str(data.get('season')).strip()
    except (TypeError, ValueError):
        abort(400)

    season = Season.by_season(season_string)
    if season is None:
        flash(f"Could not find season {season_string} in database.", category='error')
        abort(404)

    general = General.get()
    if general is None:
        General.create(season)
    else:
        general.season_id = season.id

    db.session.commit()
    flash(f"Season {season.display_name} is now active.", category='success')

    return jsonify({}), 200

@admin.route('/toggle-late-modification', methods=['POST'])
@login_required
@admin_required
def endpoint_toggle_late_modification() -> Response:
    """Toggle whether late modification of tips is allowed."""

    general = General.get()
    if general is None:
        flash("No general table exists.", category='error')
        abort(404)

    general.allow_late_modification = not general.allow_late_modification
    db.session.commit()

    return jsonify({}), 200

@admin.route('/set-user-admin', methods=['POST'])
@login_required
@admin_required
def endpoint_set_user_admin() -> Response:
    """Set a user as admin given their UUID."""

    if not request.is_json:
        abort(415)
    data = request.get_json()

    try:
        uuid = str(data.get('uuid')).strip()
    except (TypeError, ValueError):
        abort(400)

    if not uuid:
        flash("UUID was empty or None.", category='error')
        abort(400)

    user = User.by_id(uuid)
    if user:
        user.is_admin = True
        db.session.commit()
        flash(f"User {user.username} is now an admin.", category='success')
    else:
        flash(f"User with ID: {uuid} not found", category='error')

    return jsonify({}), 200

def _parse_headers(headers: dict) -> None:
    """Update the General table with info from the API response headers."""

    data = {
        'last_update': datetime.datetime.now(),
        'remaining_requests':  headers.get('X-Requests-Available-Minute', None)
    }
    General.update(**data)

@admin.route('/toggle-holiday-theme', methods=['POST'])
@login_required
@admin_required
def endpoint_toggle_holiday_theme() -> Response:
    """Toggle whether late modification of tips is allowed."""

    general = General.get()
    if general is None:
        flash("No general table exists.", category='error')
        abort(404)

    general.holiday_theme = not general.holiday_theme
    db.session.commit()

    return jsonify({}), 200
