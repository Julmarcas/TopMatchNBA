from datetime import datetime
from datetime import timedelta
import time
import os
from topmatchnba.main import (
    fetch_nba_game_data,
    calculate_game_punctuation,
    generate_json_for_games,
)


def retry_failed_dates():
    # Attempt to open the file with failed dates. If it doesn't exist, exit the function.
    try:
        with open("failed_dates.txt", "r") as file:
            failed_dates = file.readlines()
    except FileNotFoundError:
        print("No failed dates file found. Exiting retry function.")
        return

    new_failed_dates = []  # List to keep track of dates that fail during the retry

    for date_str in failed_dates:
        date_str = date_str.strip()  # Remove any newline characters or whitespace
        try:
            # Convert the string back to a datetime object
            date = datetime.strptime(date_str, "%Y-%m-%d")
            print(f"Retrying data fetch for: {date.strftime('%Y-%m-%d')}")

            # Fetch the data for the given date
            games = fetch_nba_game_data(date)

            for game in games.values():
                game.game_punctuation = calculate_game_punctuation(game)

            sorted_games = sorted(
                games.values(), key=lambda game: game.game_punctuation, reverse=True
            )

            # Generate the output file name based on the date
            output_file = f"data/topmatchnba-{date.strftime('%d-%m-%Y')}.json"
            generate_json_for_games(sorted_games, output_file)

            # Sleep for 5 seconds after each successful call to respect API limits
            time.sleep(5)

        except Exception as e:
            print(f"Error retrying data fetch for {date.strftime('%Y-%m-%d')}: {e}")
            new_failed_dates.append(date_str)  # Save the date again for future retries

    # If there are any new failed dates, save them; otherwise, indicate completion
    if new_failed_dates:
        with open("failed_dates.txt", "w") as file:
            for date in new_failed_dates:
                file.write(f"{date}\n")
        print("Updated failed dates have been saved to 'failed_dates.txt'.")
    else:
        print("All retries succeeded. No failed dates remaining.")
        os.remove("failed_dates.txt")


def fetch_season_data(start_date: datetime, end_date: datetime):
    current_date = start_date
    failed_dates = []  # List to keep track of failed requests

    while current_date <= end_date:
        try:
            print(f"Fetching data for: {current_date.strftime('%Y-%m-%d')}")
            games = fetch_nba_game_data(current_date)

            for game in games.values():
                game.game_punctuation = calculate_game_punctuation(game)

            sorted_games = sorted(
                games.values(), key=lambda game: game.game_punctuation, reverse=True
            )

            output_file = f"data/topmatchnba-{current_date.strftime('%d-%m-%Y')}.json"
            generate_json_for_games(sorted_games, output_file)

            # Sleep for 5 seconds after each successful call
            time.sleep(5)

        except Exception as e:
            print(f"Error fetching data for {current_date.strftime('%Y-%m-%d')}: {e}")
            failed_dates.append(
                current_date.strftime("%Y-%m-%d")
            )  # Add the failed date to the list

        current_date += timedelta(days=1)

    # Save the failed dates to a file for retrying later
    if failed_dates:
        with open("failed_dates.txt", "w") as file:
            for date in failed_dates:
                file.write(f"{date}\n")
        print("Failed dates have been saved to 'failed_dates.txt'.")


def main():
    # season_start_date = datetime(2023, 10, 24)
    # today = (
    #     datetime.now()
    # )  # Adjust as necessary if you want to set a different end date
    # fetch_season_data(season_start_date, today)
    retry_failed_dates()


if __name__ == "__main__":
    main()
