import json
import os
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

from fp.fp import FreeProxy
from nba_api.stats.endpoints import scoreboardv2


@dataclass
class Team:
    team_id: str
    team_abbreviation: str = ""
    team_city_name: str = ""
    team_name: str = ""
    conference: str = ""
    conference_position: int = 0


@dataclass
class Game:
    date: datetime
    game_id: str
    home_team: Team
    visitor_team: Team
    home_team_points: int = 0
    visitor_team_points: int = 0
    game_punctuation: int = 0
    maximum_points_player: int = 0


def process_game_headers(games, game_headers):
    """
    Processes game headers and creates a new game.
    """
    for game_header in game_headers:
        game = Game(
            date=datetime.fromisoformat(game_header[0]),
            game_id=game_header[2],
            home_team=Team(team_id=game_header[6]),
            visitor_team=Team(team_id=game_header[7]),
        )
        games[game.game_id] = game


def process_line_scores(games, line_scores):
    """
    Processes line scores and associates them with corresponding games.
    """
    for line_score in line_scores:
        game_id = line_score[2]
        team_id = line_score[3]
        game = games.get(game_id)

        if not game:
            continue

        if game.home_team.team_id == team_id:
            game.home_team.team_abbreviation = line_score[4]
            game.home_team.team_city_name = line_score[5]
            game.home_team.team_name = line_score[6]
            game.home_team_points = line_score[22]
        else:
            game.visitor_team.team_abbreviation = line_score[4]
            game.visitor_team.team_city_name = line_score[5]
            game.visitor_team.team_name = line_score[6]
            game.visitor_team_points = line_score[22]


def process_team_leaders(games, team_leaders):
    """
    Processes team leaders and updates the maximum points of a player.
    """
    for team_leader in team_leaders:
        game_id = team_leader[0]
        for game in games.values():
            if game.game_id == game_id:
                if team_leader[7] >= game.maximum_points_player:
                    game.maximum_points_player = team_leader[7]


def process_conf_standings(games, conf_standings):
    """
    Processes conference standings and associates them with corresponding games.
    """
    for index, conf_standing in enumerate(conf_standings):
        team_id = conf_standing[0]
        for game in games.values():
            if game.home_team.team_id == team_id:
                game.home_team.conference = conf_standing[4]
                game.home_team.conference_position = index + 1
            if game.visitor_team.team_id == team_id:
                game.visitor_team.conference = conf_standing[4]
                game.visitor_team.conference_position = index + 1


def fetch_nba_game_data(game_date: datetime) -> dict[str, Game]:
    """
    Fetches NBA game data for a given date and returns a dictionary of games.
    """

    proxy = FreeProxy().get()

    try:
        scoreboard = scoreboardv2.ScoreboardV2(
            day_offset=0, game_date=game_date, proxy=proxy
        )
    except Exception as e:
        raise RuntimeError(f"Failed to fetch NBA data: {e}") from e

    games: dict[str, Game] = {}
    game_headers = scoreboard.game_header.get_dict().get("data", [])
    line_scores = scoreboard.line_score.get_dict().get("data", [])
    east_conf_standings = scoreboard.east_conf_standings_by_day.get_dict().get(
        "data", []
    )
    west_conf_standings = scoreboard.west_conf_standings_by_day.get_dict().get(
        "data", []
    )
    team_leaders = scoreboard.team_leaders.get_dict().get("data", [])

    # print(scoreboard.get_json())

    # Process line scores, conference standings, and team leaders
    process_game_headers(games, game_headers)
    process_line_scores(games, line_scores)
    process_team_leaders(games, team_leaders)
    process_conf_standings(games, east_conf_standings)
    process_conf_standings(games, west_conf_standings)

    return games


def calculate_game_punctuation(game: Game) -> int:
    """
    Calculate the points of a match based on various statistics.
    """
    game_punctuation = 0

    # score diff
    score_diff = abs(game.home_team_points - game.visitor_team_points)
    if score_diff < 5:
        game_punctuation += 8
    elif score_diff < 10:
        game_punctuation += 4
    elif score_diff < 15:
        game_punctuation += 2

    # standings
    if (
        game.home_team.conference_position <= 3
        and game.visitor_team.conference_position <= 3
    ):
        game_punctuation += 6
    elif (
        game.home_team.conference_position <= 7
        and game.visitor_team.conference_position <= 7
    ):
        game_punctuation += 4
    elif game.home_team.conference_position <= 3:
        game_punctuation += 2
    elif game.visitor_team.conference_position <= 3:
        game_punctuation += 2

    # maximum points of a player
    if game.maximum_points_player > 50:
        game_punctuation += 4
    elif game.maximum_points_player > 40:
        game_punctuation += 2

    return game_punctuation


def generate_json_for_games(games, output_file="games.json"):
    data = []
    for game in games:
        game_dict = asdict(game)
        game_dict["date"] = game.date.isoformat()
        data.append(
            {
                "game": game_dict,
                "game_punctuation": game.game_punctuation,
            }
        )

    current_dir = os.path.dirname(__file__)
    json_file_path = os.path.join(current_dir, "..", "public", output_file)

    with open(json_file_path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def main():
    # specific_date = datetime(2023, 11, 16)

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    games = fetch_nba_game_data(yesterday)

    for game in games.values():
        game.game_punctuation = calculate_game_punctuation(game)

    sorted_games = sorted(
        games.values(), key=lambda game: game.game_punctuation, reverse=True
    )

    for game in sorted_games:
        print(
            f"{game.home_team.team_name} - {game.visitor_team.team_name}: Points {game.game_punctuation}"
        )

    output_file = f"data/topmatchnba-{yesterday.strftime('%d-%m-%Y')}.json"

    generate_json_for_games(sorted_games, output_file)


if __name__ == "__main__":
    main()
