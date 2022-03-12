from flask import Blueprint, flash, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import User, Note, Tip
from . import db
import datetime
import json
import os

views = Blueprint("views", __name__)
curr_folder = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(curr_folder, 'data_all.json')


@views.route("/")
def home():
    with open(file) as f:
        data = json.load(f)

    time = datetime.datetime.now()
    y = time.strftime("%Y")
    m = time.strftime("%m")
    d = time.strftime("%d")
    start_date = "{}-{}-{}".format(y, m, d)
    end_date = str(time + datetime.timedelta(days=7)).split()[0]

    return render_template("index.html", user=current_user, date=[start_date, end_date], data=data["result"])


@views.route("/fixtures", methods=["GET", "POST"])
@login_required
def fixtures():
    with open(file) as f:
        data = json.load(f)

    time = datetime.datetime.now()
    start_date, end_date = get_dates(time)

    if request.method == "POST":
        for key in request.form:
            if key == "date-start":
                start_date = request.form[key]
            elif key == "date-end":
                end_date = request.form[key]
            else:
                event_key = int(key.split("-")[1])
                tip = request.form[key]

                if (len(tip) < 1 or len(tip) > 1):
                    flash("Något gick fel", category="error")
                else:
                    new_tip = Tip(event_key=event_key, tip=tip,
                                  user_id=current_user.id)
                    db.session.add(new_tip)
                    db.session.commit()
                    flash("Tippning regristrerad", category="success")
                    print(f"Added tip for {event_key}: {tip}")

    if start_date > end_date:
        flash("Slutdatum kan inte vara innan startdatum", category="error")
        start_date, end_date = get_dates(time)

    return render_template("fixtures.html", user=current_user, users=User.query.all(), date=[start_date, end_date], data=data["result"])


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
            flash("Tip borttaget", category="success")

    return jsonify({})


def get_dates(time):
    y = time.strftime("%Y")
    m = time.strftime("%m")
    d = time.strftime("%d")
    start_date = "{}-{}-{}".format(y, m, d)
    end_date = str(time + datetime.timedelta(days=14)).split()[0]

    return start_date, end_date
