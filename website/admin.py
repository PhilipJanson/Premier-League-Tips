"""Admin."""

import datetime
import time

from flask import Blueprint, Response, render_template, flash, redirect, jsonify, url_for
from flask_login import login_required, current_user

from .models import User, General, Fixture
from .schemas import FixtureSchema
from .utils import api_call

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def endpoint_admin() -> str:
    """Page to display options for an admin user."""

    if not current_user.is_admin:
        flash("Adminprivilegier krävs", category='error')
        return redirect(url_for('views.endpoint_home'))

    kwargs = {
        'season': General.get_active_season(),
        'user': current_user,
        'all_users': User.all(),
        'general': General.get()
    }
    return render_template('admin.html', **kwargs)

@admin.route('/fetch-api-data', methods=['POST'])
def endpoint_fetch_api_data() -> Response:
    """Fetch data from the API and update the database."""

    if not current_user.is_admin:
        flash("Adminprivilegier krävs", category='error')
        return jsonify({})

    print("Strarting task to fetch API data...")
    # TODO: Make season selectable from the admin page
    season = '2025'
    start_time = time.perf_counter()

    try:
        headers, fixture_response = api_call('fixtures', season)
        schema = FixtureSchema(context={"season": season})
        __parse_headers(headers)

        for fixture_json in fixture_response['response']:
            fixture = schema.load(fixture_json)
            Fixture.create_or_update(fixture)

        end_time = time.perf_counter()
        flash(f"Task finished in {(end_time - start_time):.2f} seconds.", category='success')
    except Exception as error:
        end_time = time.perf_counter()
        flash(f"Task failed in {(end_time - start_time):.2f} seconds: "
              f"{type(error).__name__}", category='error')
        print(error)

    print(f"Task finished in {(end_time - start_time):.2f} seconds.")
    return jsonify({})

def __parse_headers(headers: dict) -> None:
    """Update the General table with info from the API response headers."""

    data = {
        'season': General.get_active_season(),
        'last_update': datetime.datetime.now(),
        'remaining_requests':  headers['x-ratelimit-requests-remaining']
    }
    General.update(**data)
