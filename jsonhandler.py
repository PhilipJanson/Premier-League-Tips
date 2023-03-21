from website import db
from website.models import User, Fixture, Tip
import os
import json

curr_folder = os.path.dirname(os.path.abspath(__file__))
tip_file = os.path.join(curr_folder, 'website/data/tips.json')

def read_tip():
    with open(tip_file) as f:
        tips_data = json.load(f)

    for username in tips_data["users"]:
        user = User.query.filter_by(username=username["name"]).first()

        for tip in username["tips"]:
            fixture_id = tip["fixture_id"]
            value = tip["tip"]
            fixture = Fixture.query.filter_by(fixture_id=fixture_id).first()

            if fixture is not None:
                new_tip = Tip.query.filter_by(user_id=user.id).filter_by(
                    fixture_id=fixture_id).first()

                if new_tip is None:
                    new_tip = Tip(fixture_id=fixture_id, tip=value,
                                  correct=0, user_id=user.id)
                    db.session.add(new_tip)
                else:
                    new_tip.tip = value

    db.session.commit()

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

    with open(tip_file, "w") as f:
        json.dump(data, f)