from flask import Blueprint, flash, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Tip
from . import db
import datetime
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
    with open(fixture_file) as f:
        fixtures_data = json.load(f)

    time = datetime.datetime.now()
    start_date, end_date = get_dates(time, 7)

    return render_template("index.html", user=current_user, date=[start_date, end_date], fixtures_data=fixtures_data["response"])


@views.route("/fixtures", methods=["GET", "POST"])
@login_required
def fixtures():
    with open(fixture_file) as f:
        fixtures_data = json.load(f)

    time = datetime.datetime.now()
    start_date, end_date = get_dates(time, 14)

    if request.method == "POST":
        form = request.form

        for key in form:
            if key == "date-start":
                start_date = form[key]
            elif key == "date-end":
                end_date = form[key]
            else:
                fixture_id = int(key.split("-")[1])
                tip = form[key]

                if (len(tip) < 1 or len(tip) > 1):
                    flash("Något gick fel", category="error")
                else:
                    in_database = False

                    for usertips in current_user.tips:
                        if fixture_id == usertips.fixture_id:
                            in_database = True

                    if in_database:
                        flash("Du har redan tippat den här matchen",
                              category="error")
                    else:
                        new_tip = Tip(fixture_id=fixture_id, tip=tip,
                                      user_id=current_user.id)
                        db.session.add(new_tip)
                        db.session.commit()
                        write_tip()
                        flash("Tippning regristrerad", category="success")

    if start_date > end_date:
        flash("Slutdatum kan inte vara innan startdatum", category="error")
        start_date, end_date = get_dates(time, 14)

    return render_template("fixtures.html", user=current_user, date=[start_date, end_date], fixtures_data=fixtures_data["response"], users=User.query.all())


@views.route("/standings")
@login_required
def standings():
    with open(standings_file) as f:
        standings_data = json.load(f)

    return render_template("standings.html", user=current_user, standings_data=standings_data["response"])


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
    with open(fixture_file) as f:
        fixtures_data = json.load(f)

    u = current_user

    if request.method == "POST":
        username = request.form["form-username"]
        u = User.query.filter_by(username=username).first()

    return render_template("tips.html", user=current_user, fixtures_data=fixtures_data["response"], u=u, users=User.query.all())


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
        new_tip = Tip(fixture_id=fixture_id, tip=tip,
                      user_id=user.id)
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


def get_dates(time, days):
    y = time.strftime("%Y")
    m = time.strftime("%m")
    d = time.strftime("%d")
    start_date = "{}-{}-{}".format(y, m, d)
    end_date = str(time + datetime.timedelta(days=days)).split()[0]

    return start_date, end_date
