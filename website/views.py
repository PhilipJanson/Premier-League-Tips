from flask import Blueprint, flash, render_template, request, jsonify
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


@views.route("/")
def home():
    with open(fixture_file) as f:
        data = json.load(f)

    time = datetime.datetime.now()
    start_date, end_date = get_dates(time, 7)

    return render_template("index.html", user=current_user, date=[start_date, end_date], data=data["response"])


@views.route("/fixtures", methods=["GET", "POST"])
@login_required
def fixtures():
    with open(fixture_file) as f:
        data = json.load(f)

    time = datetime.datetime.now()
    start_date, end_date = get_dates(time, 14)

    if request.method == "POST":
        for key in request.form:
            if key == "date-start":
                start_date = request.form[key]
            elif key == "date-end":
                end_date = request.form[key]
            else:
                fixture_id = int(key.split("-")[1])
                tip = request.form[key]

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

    return render_template("fixtures.html", user=current_user, users=User.query.all(), date=[start_date, end_date], data=data["response"])


@views.route("/standings")
@login_required
def standings():
    with open(standings_file) as f:
        data = json.load(f)

    return render_template("standings.html", user=current_user, data=data["response"])


@views.route("/tips")
@login_required
def tips():
    return render_template("tips.html", user=current_user, users=User.query.all())


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

        user_data[user.username] = tip_list
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
