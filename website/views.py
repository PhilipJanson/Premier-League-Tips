from flask import Blueprint, flash, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Tip, Fixture, Team, Result, General
from datetime import datetime, timedelta, date
from . import db
import json

views = Blueprint("views", __name__)

@views.route("/")
def home() -> str:
    start, end = get_week_dates()
    fixtures = get_date_fixtures(get_season(), start, end)
    return render("index", user=current_user, fixtures=fixtures)

@views.route("/tip/<response>")
@login_required
def tip(response) -> str:
    if response == "register":
        flash("Tippning regristrerad")

    id = get_nearest_fixture(datetime.now())
    fixtures = get_fixtures(get_season())
    return render("tip", user=current_user, id=id, fixtures=fixtures, allow_post=False)

@views.route("/fixtures")
@login_required
def fixtures() -> str:
    id = get_nearest_fixture(datetime.now())
    fixtures = get_fixtures(get_season())
    tip_ids = [tip.fixture_id for tip in current_user.tips]
    return render("fixtures", user=current_user, users=User.query.all(), tip_ids=tip_ids, id=id, fixtures=fixtures)

@views.route("/standings/<season>")
@login_required
def standings(season) -> str:
    teams = Team.query.filter_by(season=season).order_by(Team.rank)
    return render("standings", user=current_user, teams=teams)

@views.route("/stats/<season>")
@login_required
def stats(season) -> str:
    fixtures = get_fixtures(season).filter_by(status="NS")
    results = Result.query.filter_by(season=season)
    return render("stats", user=current_user, users=User.query.all(), fixtures=fixtures, results=results)

@views.route("/tips", methods=["GET", "POST"])
@login_required
def tips() -> str:
    u = current_user

    if request.method == "POST":
        username = request.form["form-username"]
        u = User.query.filter_by(username=username).first()

    return render("tips", user=current_user, fixtures=get_fixtures(get_season()), u=u, users=User.query.all())

@views.route("/teampicker")
@login_required
def teampicker() -> str:
    teams = Team.query.filter_by(season=get_season()).order_by(Team.name)
    return render("teampicker", user=current_user, teams=teams)

@views.route("/admin", methods=["GET", "POST"])
@login_required
def admin() -> str:
    if request.method == "POST":
        form = request.form
        data = []

        for key in form:
            data.append(form[key])

        if data[1]:
            user = User.query.filter_by(username=data[0]).first()
            new_tip = Tip(fixture_id=data[1], tip=data[2],
                          user_id=user.id)
            db.session.add(new_tip)
            db.session.commit()
        else:
            flash("Ingen ID angiven", category="error")

    if (current_user.is_admin):
        return render("admin", user=current_user, users=User.query.all())
    else:
        return redirect(url_for("views.home"))
    
@views.route("/register-tips", methods=["POST"])
def register_tips() -> str:
    tips = json.loads(request.data)

    for tip in tips:
        fixture_id = int(tip[0].strip())
        value = tip[1].strip()
        prev_tip = Tip.query.filter_by(user_id=current_user.id).filter_by(
            fixture_id=fixture_id).first()

        if prev_tip is None:
            new_tip = Tip(tip=value, correct=0,
                          fixture_id=fixture_id, user_id=current_user.id)
            db.session.add(new_tip)
        else:
            prev_tip.tip = value

    db.session.commit()

    return jsonify({})

def get_date_fixtures(season, start, end):
    return get_fixtures(season).filter(Fixture.date >= start).filter(Fixture.date <= end)

def get_fixtures(season):
    return Fixture.query.filter_by(season=season)

def get_week_dates():
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return str(start), str(end)

def get_nearest_fixture(date):
    dates = [datetime.strptime(fixture.date + fixture.time, '%Y-%m-%d%H:%M')
             for fixture in Fixture.query.all()]
    nearest = min(dates, key=lambda x: abs(x - date))

    for fixture in Fixture.query.all():
        if nearest == datetime.strptime(fixture.date + fixture.time, '%Y-%m-%d%H:%M'):
            id = fixture.fixture_id

    return id

def get_season():
    general = General.query.first()
    
    if general is None:
        return "2024"
    
    return general.season

def render(html_name, **kwargs):
    return render_template(f"{html_name}.html", season=get_season(), **kwargs)
