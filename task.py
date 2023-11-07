from website import create_app
from website.models import User, Fixture, Team, Tip, Result, General
from website import db
from keys import API_KEY
from jsonhandler import read_tip, write_tip
import requests
import time

# Premier League
LEAGUE_ID = 39

# Do not change unless a new season is beginning
SEASON = 2023

def api_call(endpoint, season):
    url = f"https://v3.football.api-sports.io/{endpoint}?season={season}&league={LEAGUE_ID}"

    if endpoint == "fixtures":
        url = url + "&timezone=Europe/Stockholm"

    payload = {
    }

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    update_general(response.headers)
    return response.json()["response"]

def update_general(headers):
    general = General.query.first()

    if general is None:
        new_general = General(season=SEASON, last_update=headers["Date"], remaining_requests=int(headers["x-ratelimit-requests-remaining"]))
        db.session.add(new_general)
    else:
        general.season = SEASON
        general.last_update = headers["Date"]
        general.remaining_requests = int(headers["x-ratelimit-requests-remaining"])
    
    db.session.commit()

def add_standings(response, season):
    for leagues in response:
        for temp in leagues["league"]["standings"]:
            for team in temp:
                handle_team(team, season)

    db.session.commit()

def handle_team(team, season):
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

    t = Team.query.filter_by(season=season).filter_by(name=name).first()

    if t is None:
        new_team = Team(season=season, name=name, logo=logo, rank=rank, points=points, games_played=games_played, wins=wins,
                        draws=draws, losses=losses, goals_scored=goals_scored, goals_conceded=goals_conceded, form=form)
        db.session.add(new_team)
    else:
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

def add_fixtures(response, season):
    sorted_fixtures = sorted(response, key=lambda x: x['fixture']['date'])

    for fixtures in sorted_fixtures:
        handle_fixture(fixtures, season)

    db.session.commit()

def handle_fixture(fixtures, season):
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
        new_fixture = Fixture(fixture_id=fixture_id, season=season, round=round, date=date, time=time, status=status,
                              home_team_id=home_team_id, away_team_id=away_team_id, home_score=home_score, away_score=away_score)
        db.session.add(new_fixture)
    else:
        f.round = round
        f.date = date
        f.time = time
        f.status = status
        f.home_score = home_score
        f.away_score = away_score

def calc_results(season):
    for user in User.query.all():
        total = 0
        finished = 0
        correct = 0
        incorrect = 0
        tip_1 = 0
        tip_X = 0
        tip_2 = 0
        round_scores = ""
        round_guesses = ""

        for tip in user.tips:
            fixture = Fixture.query.filter_by(season=season).filter_by(
                fixture_id=tip.fixture_id).first()

            if fixture is not None:
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
        curr_guess = 0

        for fixture in Fixture.query.filter_by(season=season).order_by(Fixture.round):
            tip = Tip.query.filter_by(user_id=user.id).filter_by(
                fixture_id=fixture.fixture_id).first()

            if curr_round != fixture.round:
                round_scores += str(curr_score) + "-"
                round_guesses += str(curr_guess) + "-"
                curr_round = fixture.round
                curr_score = 0
                curr_guess = 0

            if tip is not None:
                curr_guess += 1
                if tip.correct == 1:
                    curr_score += 1

        round_scores += str(curr_score)
        round_guesses += str(curr_guess)

        result = Result.query.filter_by(
            season=season).filter_by(user_id=user.id).first()

        if result is None:
            new_result = Result(season=season, total=total, finished=finished, correct=correct,
                                incorrect=incorrect, tip_1=tip_1, tip_X=tip_X, tip_2=tip_2, 
                                round_scores=round_scores, round_guesses=round_guesses, 
                                user_id=user.id)
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
            result.round_guesses = round_guesses

    db.session.commit()

def is_winner(fixture, tip):
    score = int(fixture.home_score) - int(fixture.away_score)
    return (score > 0 and tip == "1") or (score < 0 and tip == "2") or (score == 0 and tip == "X")

def get_season():
    general = General.query.first()
    
    if general is None:
        return SEASON
    
    return general.season

if __name__ == "__main__":
    start = time.perf_counter()
    app = create_app()
    read_old = False
    update = True

    with app.app_context():
        if read_old:
            read_tip()

        season = get_season()

        # If we want to load previous seasons 
        # fixtures and calculate their results:
        #
        # season = "2021"

        if update:
            standings_response = api_call("standings", season)
            fixture_response = api_call("fixtures", season)
            add_standings(standings_response, season)
            add_fixtures(fixture_response, season)

        calc_results(season)

        # FIX THIS
        #write_tip()

    end = time.perf_counter()
    print("Finished in:", end - start)
