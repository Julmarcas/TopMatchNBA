from datetime import datetime

import pytest

from topmatchnba.main import calculate_game_punctuation
from topmatchnba.main import Game
from topmatchnba.main import process_conf_standings
from topmatchnba.main import process_game_headers
from topmatchnba.main import process_line_scores
from topmatchnba.main import process_team_leaders
from topmatchnba.main import Team


def test_process_game_headers_empty():
    games = {}
    game_headers = []
    process_game_headers(games, game_headers)
    assert len(games) == 0


def test_process_game_headers_single_game():
    games = {}
    game_headers = [
        [
            "2024-01-07T00:00:00",
            "some_other_info",
            "game_id_123",
            "more_info",
            "more_info",
            "more_info",
            "team_id_home",
            "team_id_visitor",
        ]
    ]
    process_game_headers(games, game_headers)
    assert len(games) == 1
    assert "game_id_123" in games
    game = games["game_id_123"]
    assert game.date.isoformat() == "2024-01-07T00:00:00"
    assert game.game_id == "game_id_123"
    assert isinstance(game.home_team, Team)
    assert game.home_team.team_id == "team_id_home"
    assert isinstance(game.visitor_team, Team)
    assert game.visitor_team.team_id == "team_id_visitor"


# def test_process_game_headers_with_incomplete_data():
#     games = {}
#     # Example of incomplete data (missing team IDs)
#     game_headers = [["2024-01-06T00:00:00", "info", "game_id_123", "info"]]
#     process_game_headers(games, game_headers)
#     assert len(games) == 1
#     assert "game_id_123" in games
#     game = games["game_id_123"]
#     assert game.date.isoformat() == "2024-01-06T00:00:00"
#     assert game.game_id == "game_id_123"
#     assert game.home_team.team_id == ""
#     assert game.visitor_team.team_id == ""


def test_process_line_scores_empty():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    line_scores = []
    process_line_scores(games, line_scores)
    assert games["game_id_123"].home_team_points == 0
    assert games["game_id_123"].visitor_team_points == 0


# def test_process_line_scores_single_game():
#     games = {
#         "game_id_123": Game(
#             date=datetime.now(),
#             game_id="game_id_123",
#             home_team=Team(team_id="team_id_home"),
#             visitor_team=Team(team_id="team_id_visitor"),
#         )
#     }
#     line_scores = [
#         [
#             "date",
#             "info",
#             "game_id_123",
#             "team_id_home",
#             "HOM",
#             "HomeCity",
#             "HomeName",
#             "other_info",
#             "other_info",
#             110,
#         ],
#         [
#             "date",
#             "info",
#             "game_id_123",
#             "team_id_visitor",
#             "VIS",
#             "VisitorCity",
#             "VisitorName",
#             "other_info",
#             "other_info",
#             95,
#         ],
#     ]
#     process_line_scores(games, line_scores)
#     assert games["game_id_123"].home_team_points == 110
#     assert games["game_id_123"].visitor_team_points == 95


def test_process_line_scores_game_not_in_dict():
    games = {}
    line_scores = [
        [
            "date",
            "info",
            "game_id_123",
            "team_id_home",
            "HOM",
            "HomeCity",
            "HomeName",
            "other_info",
            "other_info",
            110,
        ]
    ]
    process_line_scores(games, line_scores)
    assert "game_id_123" not in games


def test_process_line_scores_with_malformed_data():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    # Example of malformed data (missing team points)
    line_scores = [
        [
            "date",
            "info",
            "game_id_123",
            "team_id_home",
            "HOM",
            "HomeCity",
            "HomeName",
            "other_info",
        ]
    ]
    with pytest.raises(IndexError):
        process_line_scores(games, line_scores)


def test_process_team_leaders_empty():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    team_leaders = []
    process_team_leaders(games, team_leaders)
    assert games["game_id_123"].maximum_points_player == 0


def test_process_team_leaders_single_game():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    team_leaders = [
        [
            "game_id_123",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            25,
        ],
        [
            "game_id_123",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            30,
        ],
    ]
    process_team_leaders(games, team_leaders)
    assert games["game_id_123"].maximum_points_player == 30


def test_process_team_leaders_game_not_in_dict():
    games = {}
    team_leaders = [
        [
            "game_id_123",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            25,
        ]
    ]
    process_team_leaders(games, team_leaders)
    assert "game_id_123" not in games


def test_process_team_leaders_with_malformed_data():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    # Example of malformed data (missing points data)
    team_leaders = [
        [
            "game_id_123",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
            "other_info",
        ]
    ]
    with pytest.raises(IndexError):
        process_team_leaders(games, team_leaders)


# ***********


def test_process_conf_standings_empty():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    conf_standings = []
    process_conf_standings(games, conf_standings)
    assert games["game_id_123"].home_team.conference == ""
    assert games["game_id_123"].visitor_team.conference == ""
    assert games["game_id_123"].home_team.conference_position == 0
    assert games["game_id_123"].visitor_team.conference_position == 0


def test_process_conf_standings_single_game():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    conf_standings = [
        [
            "team_id_home",
            "other_info",
            "other_info",
            "other_info",
            "East",
            "other_info",
            "other_info",
            1,
        ],
        [
            "team_id_visitor",
            "other_info",
            "other_info",
            "other_info",
            "West",
            "other_info",
            "other_info",
            2,
        ],
    ]
    process_conf_standings(games, conf_standings)
    assert games["game_id_123"].home_team.conference == "East"
    assert games["game_id_123"].visitor_team.conference == "West"
    assert games["game_id_123"].home_team.conference_position == 1
    assert games["game_id_123"].visitor_team.conference_position == 2


def test_process_conf_standings_game_not_in_dict():
    games = {}
    conf_standings = [
        [
            "team_id_home",
            "other_info",
            "other_info",
            "other_info",
            "East",
            "other_info",
            "other_info",
            1,
        ]
    ]
    process_conf_standings(games, conf_standings)
    assert "game_id_123" not in games


def test_process_conf_standings_with_malformed_data():
    games = {
        "game_id_123": Game(
            date=datetime.now(),
            game_id="game_id_123",
            home_team=Team(team_id="team_id_home"),
            visitor_team=Team(team_id="team_id_visitor"),
        )
    }
    # Example of malformed data (missing conference and position)
    conf_standings = [["team_id_home", "other_info", "other_info"]]
    with pytest.raises(IndexError):
        process_conf_standings(games, conf_standings)


def create_test_game(
    home_team_points,
    visitor_team_points,
    home_team_position,
    visitor_team_position,
    max_player_points,
):
    return Game(
        date=datetime.now(),
        game_id="test_game_id",
        home_team=Team(team_id="home_team_id", conference_position=home_team_position),
        visitor_team=Team(
            team_id="visitor_team_id", conference_position=visitor_team_position
        ),
        home_team_points=home_team_points,
        visitor_team_points=visitor_team_points,
        maximum_points_player=max_player_points,
    )


def test_calculate_game_punctuation_tight_game():
    game = create_test_game(100, 98, 5, 4, 30)
    points = calculate_game_punctuation(game)
    assert points == 12


def test_calculate_game_punctuation_large_score_diff():
    game = create_test_game(120, 90, 2, 6, 28)
    points = calculate_game_punctuation(game)
    assert points == 4


def test_calculate_game_punctuation_high_scoring_player():
    game = create_test_game(110, 105, 8, 9, 51)
    points = calculate_game_punctuation(game)
    assert points == 8


def test_calculate_game_punctuation_top_teams():
    game = create_test_game(105, 100, 3, 3, 25)
    points = calculate_game_punctuation(game)
    assert points == 10
