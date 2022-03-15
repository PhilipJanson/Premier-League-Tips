import requests
import json
import time
from keys import API_KEY

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

        with open(f"website/data/{name}.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=4)


def sort_fixtures():
    with open("website/data/fixtures.json", "r") as f:
        fixtures = json.load(f)

    sorted_fixtures = dict(fixtures)
    sorted_fixtures['response'] = sorted(
        fixtures['response'], key=lambda x: x['fixture']['date'])

    with open("website/data/fixtures.json", "w", encoding="utf-8") as f:
        json.dump(sorted_fixtures, f, indent=4)


def calc_results():
    with open("website/data/fixtures.json", "r") as f:
        fixtures_data = json.load(f)

    with open("website/data/tips.json", "r") as f:
        tips_data = json.load(f)

    results = {}
    user_list = []

    for users in tips_data["users"]:
        for user in users:
            user_data = {}
            user_data["name"] = user
            score = 0

            for fixtures in fixtures_data["response"]:
                fixture = fixtures["fixture"]

                if (fixture["status"]["short"] == "FT"):
                    for tip in users[user]:
                        tip_fixture_id = tip["fixture_id"]
                        tip_tip = tip["tip"]

                        if tip_fixture_id == fixture["id"]:
                            winner = fixtures["teams"]["home"]["winner"]
                            if is_winner(winner, tip_tip):
                                score += 1

            user_data["score"] = score
            user_list.append(user_data)

    results["users"] = user_list

    with open("website/data/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)


def is_winner(winner, tip):
    return (winner == True and tip == "1") or (winner == False and tip == "2") or (winner == None and tip == "X")


if __name__ == "__main__":
    start = time.time()
    #api_call(["fixtures", "standings", "players/topscorers"])
    sort_fixtures()
    calc_results()
    end = time.time()
    print("Finished in:", end - start)
