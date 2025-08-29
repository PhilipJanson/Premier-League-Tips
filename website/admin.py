"""Admin."""

import datetime
import json
import re
import time

from flask import Blueprint, Response, render_template, flash, redirect, jsonify, url_for, request
from flask_login import login_required, current_user

from .models import User, General, Fixture, Team, Result, Season
from .schemas import FixtureSchema, TeamSchema
from .utils import api_call, calculate_user_result
from . import db

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def endpoint_admin() -> str:
    """Page to display options for an admin user."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return redirect(url_for('views.endpoint_home'))

    kwargs = {
        'season_data': Season.get_season_data(),
        'user': current_user,
        'all_users': User.all(),
        'general': General.get()
    }
    return render_template('admin.html', **kwargs)

@admin.route('/fetch-api-fixtures', methods=['POST'])
@login_required
def endpoint_fetch_api_fixtures() -> Response:
    """Fetch fixture data from the API and update the database."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    if General.get() is None:
        flash("No general table exists.", category='error')
        return jsonify({})

    print("Starting task to fetch API fixture data...")
    season = General.get_active_season()
    start_time = time.perf_counter()

    try:
        headers, fixture_response = api_call('fixtures', season)
        schema = FixtureSchema(context={"season": season})
        __parse_headers(headers)

        for fixture_json in fixture_response['response']:
            fixture = schema.load(fixture_json)
            Fixture.create_or_update(fixture)

        db.session.commit()
        end_time = time.perf_counter()
        status = f"Task finished in {(end_time - start_time):.2f} seconds."
        flash(status, category='success')
        print(status)
    except Exception as error:
        end_time = time.perf_counter()
        flash(f"Task failed in {(end_time - start_time):.2f} seconds: "
              f"{type(error).__name__}", category='error')
        print(error)

    return jsonify({})

@admin.route('/fetch-api-standings', methods=['POST'])
@login_required
def endpoint_fetch_api_standings() -> Response:
    """Fetch standings data from the API and update the database."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    if General.get() is None:
        flash("No general table exists.", category='error')
        return jsonify({})

    print("Starting task to fetch API standings data...")
    season = General.get_active_season()
    start_time = time.perf_counter()

    try:
        headers, standings_response = api_call('standings', season)
        schema = TeamSchema(context={"season": season})
        __parse_headers(headers)

        for team_json in standings_response['response'][0]['league']['standings'][0]:
            team, standings = schema.load(team_json)
            Team.create_or_update_team_and_standing(team, standings)

        db.session.commit()
        end_time = time.perf_counter()
        status = f"Task finished in {(end_time - start_time):.2f} seconds."
        flash(status, category='success')
        print(status)
    except Exception as error:
        end_time = time.perf_counter()
        flash(f"Task failed in {(end_time - start_time):.2f} seconds: "
              f"{type(error).__name__}", category='error')
        print(error)

    return jsonify({})

@admin.route('/calculate-results', methods=['POST'])
@login_required
def endpoint_calculate_results() -> Response:
    """Fetch standings data from the API and update the database."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    if General.get() is None:
        flash("No general table exists.", category='error')
        return jsonify({})

    print("Starting task to calculate results...")
    season = General.get_active_season()
    start_time = time.perf_counter()

    for user in User.all():
        if user.username == 'admin':
            continue
        result = calculate_user_result(user, season)
        Result.create_or_update(result)

    db.session.commit()
    end_time = time.perf_counter()
    status = f"Task finished in {(end_time - start_time):.2f} seconds."
    flash(status, category='success')
    print(status)

    return jsonify({})

@admin.route('/add-season', methods=['POST'])
@login_required
def endpoint_add_season() -> Response:
    """Add a new season to the database."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    season = str(json.loads(request.data)).strip()
    if not re.fullmatch(r'^[12][0-9]{3}$', season):
        flash(f"Incorrect format for season: {season}", category='error')
        return jsonify({})

    new_season = Season.create(season)
    db.session.commit()
    flash(f"Season {new_season.display_name} created.", category='success')

    return jsonify({})

@admin.route('/set-active-season', methods=['POST'])
@login_required
def endpoint_set_active_season() -> Response:
    """Add a new season to the database."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    season_string = str(json.loads(request.data))
    season = Season.by_season(season_string)
    if season is None:
        flash(f"Could not find season {season_string} in database.", category='error')
        return jsonify({})

    general = General.get()
    if general is None:
        General.create(season)
    else:
        general.season_id = season.id

    db.session.commit()
    flash(f"Season {season.display_name} is now active.", category='success')

    return jsonify({})

@admin.route('/toggle-late-modification', methods=['POST'])
@login_required
def endpoint_toggle_late_modification() -> Response:
    """Toggle whether late modification of tips is allowed."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    general = General.get()
    if general is None:
        flash("No general table exists.", category='error')
        return jsonify({})

    general.allow_late_modification = not general.allow_late_modification
    db.session.commit()

    return jsonify({})

@admin.route('/set-user-admin', methods=['POST'])
@login_required
def endpoint_set_user_admin() -> Response:
    """Set a user as admin given their UUID."""

    if not current_user.is_admin:
        flash("Admin priviliges are needed to access this endpoint", category='error')
        return jsonify({})

    uuid = str(json.loads(request.data)).strip()
    if not uuid:
        flash("UUID was empty or None.", category='error')
        return jsonify({})

    user = User.by_id(uuid)
    if user:
        user.is_admin = True
        db.session.commit()
        flash(f"User {user.username} is now an admin.", category='success')
    else:
        flash(f"User with ID: {uuid} not found", category='error')

    return jsonify({})

def __parse_headers(headers: dict) -> None:
    """Update the General table with info from the API response headers."""

    data = {
        'last_update': datetime.datetime.now(),
        'remaining_requests':  headers['x-ratelimit-requests-remaining']
    }
    General.update(**data)
    db.session.commit()
