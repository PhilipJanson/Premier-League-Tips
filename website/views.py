from flask import Blueprint, flash, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Tip, Fixture, Team, Result
from datetime import datetime, timedelta, date
from .info import SEASON
from . import db
import json
import os

views = Blueprint("views", __name__)
curr_folder = os.path.dirname(os.path.abspath(__file__))
fixture_file = os.path.join(curr_folder, 'data/fixtures.json')
standings_file = os.path.join(curr_folder, 'data/standings.json')
tips_file = os.path.join(curr_folder, 'data/tips.json')
results_file = os.path.join(curr_folder, 'data/results.json')
p_file = os.path.join(curr_folder, 'data/old/p.txt')
t_file = os.path.join(curr_folder, 'data/old/t.txt')


@views.route("/")
def home():
    start, end = get_week_dates()
    return render_template("index.html", user=current_user, fixtures=get_date_fixtures(SEASON, start, end))


@views.route("/tip/<response>")
@login_required
def tip(response):
    if response == "register":
        flash("Tippning regristrerad")

    return render_template("tip.html", user=current_user, id=getIdFromDate(datetime.now()), fixtures=get_fixtures(SEASON))


@views.route("/register-tips", methods=["POST"])
def register_tips():
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


@views.route("/stats2/<season>")
@login_required
def stats2(season):
    return render_template("stats2.html", user=current_user, users=User.query.all(), results=Result.query.filter_by(season=season))


@views.route("/fixtures", methods=["GET", "POST"])
@login_required
def fixtures():
    return render_template("fixtures.html", user=current_user, fixtures=Fixture.query.all(), users=User.query.all())


@views.route("/standings/<season>")
@login_required
def standings(season):
    return render_template("standings.html", user=current_user, teams=Team.query.filter_by(season=season).order_by(Team.rank))


@views.route("/stats")
@login_required
def stats():
    with open(fixture_file) as f:
        fixtures_data = json.load(f)

    with open(results_file) as f:
        results_data = json.load(f)

    return render_template("stats.html", user=current_user, fixtures_data=fixtures_data["response"], results_data=results_data["users"], users=User.query.all())


@views.route("/tips", methods=["GET", "POST"])
@login_required
def tips():
    u = current_user

    if request.method == "POST":
        username = request.form["form-username"]
        u = User.query.filter_by(username=username).first()

    return render_template("tips.html", user=current_user, fixtures=get_fixtures(SEASON), u=u, users=User.query.all())


@views.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
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
            write_tip()
        else:
            flash("Ingen ID angiven", category="error")

    if (current_user.is_admin):
        return render_template("admin.html", user=current_user, users=User.query.all())
    else:
        return redirect(url_for("views.home"))


@views.route("/delete-tip", methods=["POST"])
def delete_tip():
    tip = json.loads(request.data)
    tip_id = tip["tip_id"]
    tip = Tip.query.get(tip_id)

    if tip:
        if tip.user_id == current_user.id:
            db.session.delete(tip)
            db.session.commit()
            write_tip()
            flash("Tip borttaget", category="success")

    return jsonify({})


@views.route("/load-tips", methods=["POST"])
def load_tips():
    p = open(p_file, "r")
    user = User.query.filter_by(username="philip").first()

    for line in p:
        data = str(line).split(":")
        fixture_id = data[0]
        tip = data[1].replace("\n", "")
        new_tip = Tip(fixture_id=fixture_id, tip=tip,
                      user_id=user.id)
        db.session.add(new_tip)

    t = open(t_file, "r")
    user = User.query.filter_by(username="totte").first()

    for line in t:
        data = str(line).split(":")
        fixture_id = data[0]
        tip = data[1].replace("\n", "")
        new_tip = Tip(fixture_id=fixture_id, tip=tip, user_id=user.id)
        db.session.add(new_tip)

    db.session.commit()
    write_tip()

    return jsonify({})


def write_tip():
    data = {}
    user_list = []

    for user in User.query.all():
        user_data = {}
        tip_list = []

        for tip in user.tips:
            tip_data = {}
            tip_data["fixture_id"] = tip.fixture_id
            tip_data["tip"] = tip.tip
            tip_list.append(tip_data)

        user_data["name"] = user.username
        user_data["tips"] = tip_list
        user_list.append(user_data)

    data["users"] = user_list

    with open(tips_file, "w") as f:
        json.dump(data, f)


def get_date_fixtures(season, start, end):
    return get_fixtures(season).filter(Fixture.date >= start).filter(Fixture.date <= end)


def get_fixtures(season):
    return Fixture.query.filter_by(season=season)


def get_week_dates():
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return str(start), str(end)


def getIdFromDate(date):
    dates = [datetime.strptime(fixture.date + fixture.time, '%Y-%m-%d%H:%M')
             for fixture in Fixture.query.all()]
    nearest = min(dates, key=lambda x: abs(x - date))

    for fixture in Fixture.query.all():
        if nearest == datetime.strptime(fixture.date + fixture.time, '%Y-%m-%d%H:%M'):
            id = fixture.fixture_id

    return id
