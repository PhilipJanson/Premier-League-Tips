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
                    flash("Something went wrong", category="error")
                else:
                    new_tip = Tip(event_key=event_key, tip=tip,
                                  user_id=current_user.id)
                    db.session.add(new_tip)
                    db.session.commit()
                    print(f"Added tip for {event_key}: {tip}")

    if start_date > end_date:
        flash("Slutdatum kan inte vara innan startdatum", category="error")
        start_date, end_date = get_dates(time)

    return render_template("fixtures.html", user=current_user, date=[start_date, end_date], data=data["result"])


@views.route("/tips")
@login_required
def tips():
    return render_template("tips.html", user=current_user, users=User.query.all())


@views.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if request.method == "POST":
        note = request.form.get("note")

        if len(note) < 1:
            flash("Note is empty", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Note added", category="success")

    return render_template("notes.html", user=current_user)


@views.route("/delete-note", methods=["POST"])
def delete_note():
    note = json.loads(request.data)
    note_id = note["noteId"]
    note = Note.query.get(note_id)

    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


def get_dates(time):
    y = time.strftime("%Y")
    m = time.strftime("%m")
    d = time.strftime("%d")
    start_date = "{}-{}-{}".format(y, m, d)
    end_date = str(time + datetime.timedelta(days=14)).split()[0]

    return start_date, end_date
