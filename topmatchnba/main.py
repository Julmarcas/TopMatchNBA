from datetime import datetime, timedelta
from dataclasses import dataclass
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
    game_points: int = 0
    maximum_points_player: int = 0


def fetch_nba_game_data(game_date: datetime) -> dict[str, Game]:
    try:
        scoreboard = scoreboardv2.ScoreboardV2(day_offset=0, game_date=game_date)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch NBA data: {e}") from e

    games: dict[Game] = {}
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

    for game_header in game_headers:
        game = Game(
            date=datetime.fromisoformat(game_header[0]),
            game_id=game_header[2],
            home_team=Team(team_id=game_header[6]),
            visitor_team=Team(team_id=game_header[7]),
        )
        games[game.game_id]: dict[str, Game] = game

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

    for index, east_conf_standing in enumerate(east_conf_standings):
        team_id = east_conf_standing[0]
        for game in games.values():
            if game.home_team.team_id == team_id:
                game.home_team.conference = east_conf_standing[4]
                game.home_team.conference_position = index + 1
            if game.visitor_team.team_id == team_id:
                game.visitor_team.conference = east_conf_standing[4]
                game.visitor_team.conference_position = index + 1

    for index, west_conf_standings in enumerate(west_conf_standings):
        team_id = west_conf_standings[0]
        for game in games.values():
            if game.home_team.team_id == team_id:
                game.home_team.conference = west_conf_standings[4]
                game.home_team.conference_position = index + 1
            if game.visitor_team.team_id == team_id:
                game.visitor_team.conference = west_conf_standings[4]
                game.visitor_team.conference_position = index + 1

    for team_leader in team_leaders:
        game_id = team_leader[0]
        for game in games.values():
            if game.game_id == game_id:
                if team_leader[7] >= game.maximum_points_player:
                    game.maximum_points_player = team_leader[7]

    return games


def calculate_game_points(game: Game) -> int:
    game_points = 0

    # score diff
    score_diff = abs((game.home_team_points - game.visitor_team_points))
    if score_diff < 5:
        game_points += 8
    elif score_diff < 10:
        game_points += 4
    elif score_diff < 15:
        game_points += 2

    # standings
    if (
        game.home_team.conference_position <= 3
        and game.visitor_team.conference_position <= 3
    ):
        game_points += 6
    elif (
        game.home_team.conference_position <= 7
        and game.visitor_team.conference_position <= 7
    ):
        game_points += 4
    elif game.home_team.conference_position <= 3:
        game_points += 2
    elif game.visitor_team.conference_position <= 3:
        game_points += 2

    # maximum points of a player
    if game.maximum_points_player > 50:
        game_points += 4
    elif game.maximum_points_player > 40:
        game_points += 2

    return game_points


def main():
    # specific_date = datetime(2023, 11, 16)

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    games = fetch_nba_game_data(yesterday)

    for game in games.values():
        game.game_points = calculate_game_points(game)

    sorted_games = sorted(
        games.values(), key=lambda game: game.game_points, reverse=True
    )

    for game in sorted_games:
        print(
            f"{game.home_team.team_name} - {game.visitor_team.team_name}: Points {game.game_points}"
        )


if __name__ == "__main__":
    main()
