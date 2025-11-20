import argparse
import getpass
import os
from datetime import datetime
from typing import Optional

from src import __title__, __version__, __description__
from src.garmin.client.GarminClient import GarminClient
from src.garmin.model.garmin_workout_dto import GarminSport
from src.service.workout_sync_service import GarminToMyWhooshWorkoutSyncService


def run_sync_logic(
    user: Optional[str],
    password: Optional[str],
    sport: Optional[str],
    from_date: Optional[str],
    to_date: Optional[str],
):
    """
    Main function containing the application's synchronization and integration logic.
    """
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
        end_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
    except ValueError:
        print("Error: Date format must be YYYY-MM-DD.")
        return

    try:
        sport = GarminSport[sport.upper()] if sport else GarminSport.CYCLING
    except KeyError:
        available_sports = ", ".join([s.name for s in GarminSport])
        print(f"Error: sport not recognized. Valid options are: {available_sports}.")
        return

    if not user:
        user = os.getenv("GARMIN_USER")
        if not user:
            user = input("Enter Garmin username: ")

    if not password:
        password = os.getenv("GARMIN_PASSWORD")
        if not password:
            password = getpass.getpass("Enter Garmin password: ")

    print(f"Logging in with user f{user}")
    client = GarminClient(user, password)
    client.login()
    print(f"{user} has been logged")

    sync_service = GarminToMyWhooshWorkoutSyncService(client)
    sync_service.sync_and_download_workouts(
        sport=sport, from_date=start_date, to_date=end_date
    )

    print("--- Application Finished ---")


def main():
    width: int = 50

    print("=" * width)
    print(f"{__title__} v{__version__}".center(width))
    print(f"{__description__}".center(width))
    print("=" * width)
    print("\n✓ Application started successfully!")

    parser = argparse.ArgumentParser(
        description="Synchronize workout data between services.",
        epilog="Example: python main.py --user=john.doe --from_date=2025-01-01",
    )

    parser.add_argument(
        "--user", type=str, default=None, help="Service username (optional)."
    )
    parser.add_argument(
        "--password", type=str, default=None, help="Service password (optional)."
    )
    parser.add_argument(
        "--sport",
        type=str,
        default="cycling",
        help="Filter by sport type (e.g., cycling, running, cross_country_skiing). Optional.",
    )
    parser.add_argument(
        "--from_date",
        type=str,
        default=None,
        help="Start date of the synchronization range [YYYY-MM-DD] (optional).",
    )
    parser.add_argument(
        "--to_date",
        type=str,
        default=None,
        help="End date of the synchronization range [YYYY-MM-DD] (optional).",
    )

    args = parser.parse_args()

    # Call the core application logic
    run_sync_logic(args.user, args.password, args.sport, args.from_date, args.to_date)


if __name__ == "__main__":
    main()
