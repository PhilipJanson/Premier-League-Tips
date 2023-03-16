from website import create_app
from website.models import User, Fixture, Team
from website import db
from keys import API_KEY
from website.info import SEASON
import requests
import time

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
        for tip in user.tips:
            print(user.username, tip.fixture_id, tip.tip)

if __name__ == "__main__":
    start = time.perf_counter()
    app = create_app()
    update = True

    with app.app_context():
        if update:
            standings_response = api_call("standings")
            fixture_response = api_call("fixtures")

            add_standings(standings_response)
            add_fixtures(fixture_response)

        calc_results()


    end = time.perf_counter()
    print("Finished in:", end - start)
