"""Views."""

import json
from datetime import datetime
from flask import Blueprint, Response, flash, render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user
from .models import User, Tip, Fixture, Team, Result, General
from .utils import get_week_dates, calculate_next_fixture
from . import db

views = Blueprint('views', __name__)

@views.route("/")
def home() -> str:
    """Home page for the website."""

    season = get_season()
    start, end = get_week_dates()
    fixtures = Fixture.by_dates(season, start, end)
    options = {
        'season': season,
        'user': current_user,
        'fixtures': fixtures
    }

    return render_template('index.html', **options)

@views.route('/tip/<response>')
@login_required
def tip(response: str) -> str:
    """Page to display upcoming fixtures and allow users to register new tips."""

    if response == 'register':
        flash("Tippning regristrerad")

    season = get_season()
    fixtures = Fixture.by_season(season)
    options = {
        'season': season,
        'user': current_user,
        'fixtures': fixtures,
        'next_fixture': calculate_next_fixture(fixtures, datetime.now()),
        'allow_post': False
    }

    return render_template('tip.html', **options)

@views.route('/fixtures')
@login_required
def fixtures() -> str:
    """Page to dislay all fixtures for the current season and view other user's tips."""

    season = get_season()
    fixtures = Fixture.by_season(season)
    options = {
        'season': season,
        'user': current_user,
        'all_users': User.all(),
        'fixtures': fixtures,
        'next_fixture': calculate_next_fixture(fixtures, datetime.now()),
        'tip_ids': [tip.fixture_id for tip in current_user.tips]
    }

    return render_template('fixtures.html', **options)

@views.route('/standings/<season>')
@login_required
def standings(season: str) -> str:
    """Page to display all teams in a given season ordered by their rank."""

    options = {
        'season': season,
        'user': current_user,
        'teams': Team.by_rank(season)
    }

    return render_template('standings.html', **options)

@views.route('/stats/<season>')
@login_required
def stats(season: str) -> str:
    """Page to display statistics for all users."""

    fixtures = db.session.execute(db.select(Fixture)
                                  .filter_by(season=season)
                                  .filter_by(status='ns')).scalars().all()
    options = {
        'season': season,
        'user': current_user,
        'all_users': User.all(),
        'fixtures': fixtures,
        'results': Result.by_season(season)
    }

    return render_template('stats.html', **options)

@views.route('/tips', methods=['GET', 'POST'])
@login_required
def tips() -> str:
    """Page to display all tips in a season for a specific user."""

    display_user = current_user

    if request.method == 'POST':
        username = request.form['form-username']
        display_user = User.by_username(username)

    season = get_season()
    options = {
        'season': season,
        'user': current_user,
        'all_users': User.all(),
        'display_user': display_user,
        'fixtures': Fixture.by_season(season)
    }

    return render_template('tips.html', **options)

@views.route('/teampicker')
@login_required
def teampicker() -> str:
    """Work in progress page to rank the teams."""

    season = get_season()
    options = {
        'season': season,
        'user': current_user,
        'teams': Team.by_name(season)
    }

    return render_template('teampicker.html', **options)

@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin() -> str:
    """Page to display options for an admin user."""

    if not current_user.is_admin:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        form = request.form
        data = []

        for key in form:
            data.append(form[key])

        if data[1]:
            user = User.by_username(data[0])
            new_tip = Tip(fixture_id=data[1], tip=data[2], user_id=user.id)
            db.session.add(new_tip)
            db.session.commit()
        else:
            flash("Ingen ID angiven", category='error')

    options = {
        'user': current_user,
        'all_users': User.all()
    }

    return render_template('admin.html', **options)

@views.route('/register-tips', methods=['POST'])
def register_tips() -> Response:
    """Endpoint for registering a new tip for the current user."""

    tips = json.loads(request.data)

    for tip in tips:
        fixture_id = int(str(tip['fixtureId']).strip())
        value = str(tip['value']).strip()
        prev_tip = Tip.by_fixure_id(current_user, fixture_id)

        if prev_tip is None:
            new_tip = Tip(fixture_id=fixture_id, tip=value, correct=0, user_id=current_user.id)
            db.session.add(new_tip)
        else:
            prev_tip.tip = value

    db.session.commit()

    return jsonify({})

def get_season() -> str:
    """Return the current active season."""

    general = db.session.execute(db.select(General)).scalar()

    if general:
        return general.season

    return '2024'
