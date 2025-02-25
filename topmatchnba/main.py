import json
import os
from dataclasses import asdict
from datetime import datetime
from datetime import timedelta

from topmatchnba.data import fetch_nba_game_data
from topmatchnba.data import fetch_nba_play_by_play_data
from topmatchnba.data import Game
from topmatchnba.rating import calculate_game_rating


def generate_json_for_games(games: list[Game], output_file: str = "games.json") -> None:
    """
    Generate a JSON file with game data and their corresponding ratings.

    Each game is converted to a dictionary and its date is formatted as an ISO string.
    The output is written to the ../public directory relative to the current file.

    :param games: A list of Game objects.
    :param output_file: The filename for the output JSON.
    """
    data = []
    for game in games:
        game_dict = asdict(game)
        game_dict["date"] = game.date.isoformat()
        data.append(
            {
                "game": game_dict,
                "game_rating_total": game.game_rating.total,
            }
        )

    current_dir = os.path.dirname(__file__)
    json_file_path = os.path.join(current_dir, "..", "public", output_file)

    with open(json_file_path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def main(game_date=None) -> None:
    """
    Main function to fetch NBA game data, update game ratings, sort games by rating,
    print a summary, and generate a JSON output file.
    """
    if not game_date:
        today = datetime.now()
        game_date = today - timedelta(days=1)

    # Fetch games for game_date (yesterday as default)
    games: dict[str, Game] = fetch_nba_game_data(game_date)

    # Update each game with lead changes and recalculate game rating.
    for game in games.values():
        game.lead_changes = fetch_nba_play_by_play_data(game.game_id)
        # calculate_game_rating updates game.game_rating in place.
        calculate_game_rating(game)

    # Sort games in descending order of total game rating.
    sorted_games = sorted(
        games.values(), key=lambda game: game.game_rating.total, reverse=True
    )

    # Print summary of game ratings.
    for game in sorted_games:
        print(
            f"{game.home_team.team_name} - {game.visitor_team.team_name}: "
            f"Points {game.game_rating.total}"
        )

    output_file = f"data/topmatchnba-{game_date.strftime('%d-%m-%Y')}.json"
    generate_json_for_games(sorted_games, output_file)


if __name__ == "__main__":
    main()
