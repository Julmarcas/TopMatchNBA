from dataclasses import dataclass
from datetime import datetime
from typing import Any

from nba_api.stats.endpoints import playbyplayv2
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
class GameRating:
    standings: int = 0
    score_difference: int = 0
    maximum_points_player: int = 0
    change_lead: int = 0
    total: int = 0


@dataclass
class Game:
    date: datetime
    game_id: str
    home_team: Team
    visitor_team: Team
    game_rating: GameRating
    home_team_points: int = 0
    visitor_team_points: int = 0
    maximum_points_player: int = 0
    lead_changes: int = 0


def fetch_nba_game_data(game_date: datetime) -> dict[str, Game]:
    """
    Fetch NBA game data for a given date and return a dictionary mapping game IDs to Game objects.

    :param game_date: The date for which to fetch the games.
    :return: A dictionary where each key is a game ID and the value is the corresponding Game object.
    :raises RuntimeError: If fetching NBA data fails.
    """
    try:
        scoreboard = scoreboardv2.ScoreboardV2(day_offset=0, game_date=game_date)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch NBA data: {e}") from e

    games: dict[str, Game] = {}
    game_headers: list[Any] = scoreboard.game_header.get_dict().get("data", [])
    line_scores: list[Any] = scoreboard.line_score.get_dict().get("data", [])
    east_conf_standings: list[
        Any
    ] = scoreboard.east_conf_standings_by_day.get_dict().get("data", [])
    west_conf_standings: list[
        Any
    ] = scoreboard.west_conf_standings_by_day.get_dict().get("data", [])
    team_leaders: list[Any] = scoreboard.team_leaders.get_dict().get("data", [])

    process_game_headers(games, game_headers)
    process_line_scores(games, line_scores)
    process_team_leaders(games, team_leaders)
    process_conf_standings(games, east_conf_standings)
    process_conf_standings(games, west_conf_standings)

    return games


def fetch_nba_play_by_play_data(game_id: str) -> int:
    """
    Calculate the number of lead changes in a game using play-by-play data.

    The SCORE field in the JSON output is expected to be in the format 'visitor_score - home_score'.

    :param game_id: The unique identifier for the game.
    :return: The total number of lead changes.
    """
    pbp_data = playbyplayv2.PlayByPlayV2(game_id=game_id).get_dict()

    result_set = pbp_data.get("resultSets", [])[0]
    playbyplay_headers: list[str] = result_set.get("headers", [])
    playbyplay_rows: list[Any] = result_set.get("rowSet", [])

    return process_lead_changes(playbyplay_rows, playbyplay_headers)


def process_game_headers(games: dict[str, Game], game_headers: list[Any]) -> None:
    """
    Process game header data to create Game objects and store them in the games dictionary.

    :param games: Dictionary to store Game objects keyed by game ID.
    :param game_headers: List of game header data.
    """
    for game_header in game_headers:
        game = Game(
            date=datetime.fromisoformat(game_header[0]),
            game_id=game_header[2],
            home_team=Team(team_id=game_header[6]),
            visitor_team=Team(team_id=game_header[7]),
            game_rating=GameRating(),
        )
        games[game.game_id] = game


def process_line_scores(games: dict[str, Game], line_scores: list[Any]) -> None:
    """
    Process line score data and update the corresponding Game objects.

    :param games: Dictionary of Game objects.
    :param line_scores: List of line score data.
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


def process_team_leaders(games: dict[str, Game], team_leaders: list[Any]) -> None:
    """
    Process team leader data to update the maximum points scored by a player for each game.

    :param games: Dictionary of Game objects.
    :param team_leaders: List of team leader data.
    """
    for leader in team_leaders:
        game_id = leader[0]
        if game := games.get(game_id):
            # leader[7] holds the player's points
            game.maximum_points_player = max(game.maximum_points_player, leader[7])


def process_conf_standings(games: dict[str, Game], conf_standings: list[Any]) -> None:
    """
    Process conference standings and update the corresponding teams in each game.

    :param games: Dictionary of Game objects.
    :param conf_standings: List of conference standings data.
    """
    for position, standing in enumerate(conf_standings, start=1):
        team_id = standing[0]
        conference = standing[4]
        for game in games.values():
            if game.home_team.team_id == team_id:
                game.home_team.conference = conference
                game.home_team.conference_position = position
            if game.visitor_team.team_id == team_id:
                game.visitor_team.conference = conference
                game.visitor_team.conference_position = position


def process_lead_changes(
    playbyplay_rows: list[Any], playbyplay_headers: list[str]
) -> int:
    """
    Process play-by-play data to calculate the number of lead changes in a game.

    Each row's SCORE field should be in the format 'visitor_score - home_score'.

    :param playbyplay_rows: List of play-by-play data rows.
    :param playbyplay_headers: List of headers corresponding to the play-by-play data.
    :return: The total number of lead changes.
    """
    lead_changes = 0
    previous_lead = None  # Possible values: 'home', 'visitor', or 'tie'

    for row in playbyplay_rows:
        row_data = dict(zip(playbyplay_headers, row))
        score_str = row_data.get("SCORE")

        if not score_str or " - " not in score_str:
            continue

        parts = score_str.split(" - ")
        if len(parts) != 2:
            continue

        try:
            visitor_score = int(parts[0].strip())
            home_score = int(parts[1].strip())
        except (ValueError, TypeError):
            continue

        if home_score > visitor_score:
            current_lead = "home"
        elif visitor_score > home_score:
            current_lead = "visitor"
        else:
            current_lead = "tie"

        if (
            previous_lead in ("home", "visitor")
            and current_lead in ("home", "visitor")
            and current_lead != previous_lead
        ):
            lead_changes += 1

        previous_lead = current_lead

    return lead_changes
