import time
from datetime import datetime
from datetime import timedelta

from topmatchnba.main import main as game_main


def fetch_season_data(start_date: datetime, end_date: datetime):
    current_date = start_date
    failed_dates = []  # List to keep track of failed requests

    while current_date <= end_date:
        try:
            print(f"Fetching data for: {current_date.strftime('%Y-%m-%d')}")
            game_main(current_date)

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
    # season_start_date = datetime(2024, 10, 22)
    # 2025-01-06
    season_start_date = datetime(2025, 1, 6)
    today = (
        datetime.now()
    )  # Adjust as necessary if you want to set a different end date
    fetch_season_data(season_start_date, today)
    # retry_failed_dates()


if __name__ == "__main__":
    main()
