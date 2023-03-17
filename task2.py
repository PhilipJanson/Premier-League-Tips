from website import create_app
from website.models import User, Fixture, Team, Tip, Result
from website import db
from keys import API_KEY
from website.info import SEASON
import requests
import json
import time
import os

# Premier League
LEAGUE_ID = 39


def api_call(endpoint):
    url = f"https://v3.football.api-sports.io/{endpoint}?season={SEASON}&league={LEAGUE_ID}"

    if endpoint == "fixtures":
        url = url + "&timezone=Europe/Stockholm"

    payload = {
    }

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.headers)

    return response.json()["response"]


def add_standings(response):
    for leagues in response:
        for temp in leagues["league"]["standings"]:
            for team in temp:
                handle_team(team)

    db.session.commit()


def handle_team(team):
    name = team['team']['name']
    logo = team['team']['logo']
    rank = int(team['rank'])
    points = int(team["points"])
    games_played = int(team["all"]["played"])
    wins = int(team["all"]["win"])
    draws = int(team["all"]["draw"])
    losses = int(team["all"]["lose"])
    goals_scored = int(team["all"]["goals"]["for"])
    goals_conceded = int(team["all"]["goals"]["against"])
    form = team["form"]

    t = Team.query.filter_by(name=name).first()

    if t is None:
        new_team = Team(season=SEASON, name=name, logo=logo, rank=rank, points=points, games_played=games_played, wins=wins,
                        draws=draws, losses=losses, goals_scored=goals_scored, goals_conceded=goals_conceded, form=form)
        db.session.add(new_team)
    else:
        t.season = SEASON
        t.logo = logo
        t.rank = rank
        t.points = points
        t.games_played = games_played
        t.wins = wins
        t.draws = draws
        t.losses = losses
        t.goals_scored = goals_scored
        t.goals_conceded = goals_conceded
        t.form = form


def add_fixtures(response):
    sorted_fixtures = sorted(response, key=lambda x: x['fixture']['date'])

    for fixtures in sorted_fixtures:
        handle_fixture(fixtures)

    db.session.commit()


def handle_fixture(fixtures):
    fixture = fixtures["fixture"]
    fixture_id = fixture["id"]
    round = int(fixtures["league"]["round"].split(" - ")[1])
    date = fixture["date"].split("T")[0]
    time = fixture["date"].split("T")[1][0:5]
    status = fixture["status"]["short"]
    home_team = fixtures["teams"]["home"]["name"]
    home_team_id = Team.query.filter_by(name=home_team).first().id
    away_team = fixtures["teams"]["away"]["name"]
    away_team_id = Team.query.filter_by(name=away_team).first().id
    home_score = fixtures["goals"]["home"]
    away_score = fixtures["goals"]["away"]

    f = Fixture.query.filter_by(fixture_id=fixture_id).first()

    if f is None:
        new_fixture = Fixture(fixture_id=fixture_id, season=SEASON, round=round, date=date, time=time, status=status,
                              home_team_id=home_team_id, away_team_id=away_team_id, home_score=home_score, away_score=away_score)
        db.session.add(new_fixture)
    else:
        f.round = round
        f.date = date
        f.time = time
        f.status = status
        f.home_score = home_score
        f.away_score = away_score


def calc_results():
    for user in User.query.all():
        total = 0
        finished = 0
        correct = 0
        incorrect = 0
        tip_1 = 0
        tip_X = 0
        tip_2 = 0
        round_scores = ""

        for tip in user.tips:
            fixture = Fixture.query.filter_by(season=SEASON).filter_by(
                fixture_id=tip.fixture_id).first()
            total += 1

            if fixture.status == "FT":
                finished += 1

                if is_winner(fixture, tip.tip):
                    correct += 1
                    tip.correct = 1
                else:
                    incorrect += 1
                    tip.correct = -1

            if tip.tip == "1":
                tip_1 += 1
            elif tip.tip == "X":
                tip_X += 1
            elif tip.tip == "2":
                tip_2 += 1

        curr_round = 1
        curr_score = 0

        for fixture in Fixture.query.filter_by(season=SEASON).order_by(Fixture.round):
            tip = Tip.query.filter_by(user_id=user.id).filter_by(
                fixture_id=fixture.fixture_id).first()

            if curr_round != fixture.round:
                round_scores += str(curr_score) + "-"
                curr_round = fixture.round
                curr_score = 0

            if tip is not None and tip.correct == 1:
                curr_score += 1

        result = Result.query.filter_by(
            season=SEASON).filter_by(user_id=user.id).first()

        if result is None:
            new_result = Result(season=SEASON, total=total, finished=finished, correct=correct,
                                incorrect=incorrect, tip_1=tip_1, tip_X=tip_X, tip_2=tip_2, round_scores=round_scores, user_id=user.id)
            db.session.add(new_result)
        else:
            result.total = total
            result.finished = finished
            result.correct = correct
            result.incorrect = incorrect
            result.tip_1 = tip_1
            result.tip_X = tip_X
            result.tip_2 = tip_2
            result.round_scores = round_scores

    db.session.commit()


def is_winner(fixture, tip):
    score = int(fixture.home_score) - int(fixture.away_score)
    return (score > 0 and tip == "1") or (score < 0 and tip == "2") or (score == 0 and tip == "X")


def load_old_data():
    curr_folder = os.path.dirname(os.path.abspath(__file__))
    tips_file = os.path.join(curr_folder, 'website/data/tips.json')
    fixture_file = os.path.join(curr_folder, 'website/data/fixtures.json')
    standings_file = os.path.join(curr_folder, 'website/data/standings.json')

    with open(standings_file) as f:
        standings_data = json.load(f)
    add_standings(standings_data["response"])

    with open(fixture_file) as f:
        fixture_data = json.load(f)
    add_fixtures(fixture_data["response"])

    with open(tips_file) as f:
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


if __name__ == "__main__":
    start = time.perf_counter()
    app = create_app()
    update = False

    with app.app_context():
        if update:
            standings_response = api_call("standings")
            fixture_response = api_call("fixtures")

            add_standings(standings_response)
            add_fixtures(fixture_response)

        #load_old_data()
        calc_results()

    end = time.perf_counter()
    print("Finished in:", end - start)
