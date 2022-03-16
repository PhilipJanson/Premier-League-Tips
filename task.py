import requests
import json
import time
from keys import API_KEY
from matplotlib import pyplot as plt

LEAGUE_ID = 39
SEASON = 2021


def api_call(endpoints):
    for endpoint in endpoints:
        url = f"https://v3.football.api-sports.io/{endpoint}?season={SEASON}&league={LEAGUE_ID}"

        if endpoint == "fixtures":
            url = url+"&timezone=Europe/Stockholm"

        payload = {
        }

        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        name = endpoint.split("/")
        name = name[len(name) - 1]

        with open(f"website/data/{name}.json", "w") as f:
            json.dump(response.json(), f)


def sort_fixtures():
    with open("website/data/fixtures.json", "r") as f:
        fixtures = json.load(f)

    sorted_fixtures = dict(fixtures)
    sorted_fixtures['response'] = sorted(
        fixtures['response'], key=lambda x: x['fixture']['date'])

    with open("website/data/fixtures.json", "w") as f:
        json.dump(sorted_fixtures, f)


def calc_results():
    with open("website/data/fixtures.json", "r") as f:
        fixtures_data = json.load(f)

    with open("website/data/tips.json", "r") as f:
        tips_data = json.load(f)

    results = {}
    user_list = []

    for user in tips_data["users"]:
        user_data = {}
        user_data["name"] = user["name"]
        user_data["total"] = len(user["tips"])
        finished = 0
        score = 0

        for fixtures in fixtures_data["response"]:
            fixture = fixtures["fixture"]

            if (fixture["status"]["short"] == "FT"):
                for tip in user["tips"]:
                    tip_fixture_id = tip["fixture_id"]
                    tip_tip = tip["tip"]

                    if tip_fixture_id == fixture["id"]:
                        winner = fixtures["teams"]["home"]["winner"]
                        finished += 1
                        if is_winner(winner, tip_tip):
                            score += 1

        user_data["finished"] = finished
        user_data["score"] = score
        user_list.append(user_data)

    results["users"] = user_list

    results['users'] = sorted(
        results['users'], key=lambda x: x['score'], reverse=True)

    with open("website/data/results.json", "w") as f:
        json.dump(results, f)


def is_winner(winner, tip):
    return (winner == True and tip == "1") or (winner == False and tip == "2") or (winner == None and tip == "X")


def gen_stats():
    with open("website/data/results.json", "r") as f:
        result_data = json.load(f)

    for user in result_data["users"]:
        if user["score"] != 0 and user["finished"] != 0:
            labels = ['Antal rätt', 'Antal fel']
            frequency = [user["score"], user["finished"] - user["score"]]
            explode = (0.1, 0)
            colors = ((0.68627, 1, 0.65882), (1, 0.36862, 0.36862))
            fig = plt.figure()
            plt.pie(frequency, labels=labels, colors=colors, explode=explode, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            plt.savefig(f'website/static/images/stats/{user["name"]}.png')


if __name__ == "__main__":
    start = time.time()
    api_call(["fixtures", "standings"])
    sort_fixtures()
    calc_results()
    gen_stats()
    end = time.time()
    print("Finished in:", end - start)
