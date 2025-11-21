import argparse
import getpass
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from garminconnect import GarminConnectAuthenticationError
from rich.console import Console

from src import __title__, __version__, __description__
from src.garmin.client.GarminClient import GarminClient
from src.garmin.model.garmin_workout_dto import GarminSport
from src.service.workout_sync_service import GarminToMyWhooshWorkoutSyncService

console = Console()
load_dotenv()


def run_sync_logic(
        user: Optional[str],
        password: Optional[str],
        sport: Optional[str],
        from_date: Optional[str],
        to_date: Optional[str],
        output_dir: Optional[str],
        config_file: Optional[str],
):
    """
    Main function containing the application's synchronization and integration logic.
    """
    # Parse and validate input params
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
        end_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
    except ValueError:
        print("Error: Date format must be YYYY-MM-DD.")
        sys.exit(1)

    try:
        sport = GarminSport[sport.upper()] if sport else GarminSport.CYCLING
    except KeyError:
        available_sports = ", ".join([s.name for s in GarminSport])
        print(f"Error: sport not recognized. Valid options are: {available_sports}.")
        sys.exit(1)

    if not user:
        user = os.getenv("GARMIN_USER")
        if not user:
            user = input("Enter Garmin username: ")

    if not password:
        password = os.getenv("GARMIN_PASSWORD")
        if not password:
            password = getpass.getpass("Enter Garmin password: ")

    config_path = Path(config_file).expanduser() if config_file else None
    if config_path and config_path.exists():
        print(f"Using configuration from: {config_path}")
    else:
        print("Configuration file not found or not specified. Using default values.")

    if not output_dir:
        output_dir = "~/downloads/"

    output_path = Path(output_dir).expanduser()
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {output_path}")
    print(f"Files will be saved to: {output_path}")

    # Authenticate with Garmin Connect
    try:
        with console.status(f"[bold green]Logging in as '{user}'...", spinner="dots"):
            client = GarminClient(user, password)
            client.login()
        console.print(f"[green]✓[/green] Successfully logged in as '{user}'")
    except GarminConnectAuthenticationError as e:
        console.print(f"[red]✗ Login failed:[/red] {e}")
        sys.exit(1)

    # Sync and download workouts
    sync_service = GarminToMyWhooshWorkoutSyncService(client)
    sync_service.sync_and_download_workouts(
        sport=sport,
        from_date=start_date,
        to_date=end_date,
        output_dir=str(output_path),
        config_file=config_file,
    )


def default_from_date():
    return datetime.today().strftime("%Y-%m-%d")


def default_to_date():
    return (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")


def main():
    width: int = 50

    print("=" * width)
    print(f"{__title__} v{__version__}".center(width))
    print(f"{__description__}".center(width))
    print("=" * width)
    print("")

    parser = argparse.ArgumentParser(
        description="Synchronize workouts from Garmin to MyWhoosh.",
        epilog="Example: python main.py --user=john.doe@example.com --from_date=2025-01-01",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        choices=["cycling", "running", "cross_country_skiing"],
        default="cycling",
        help="Filter by sport type (optional).",
    )
    parser.add_argument(
        "--from-date",
        type=str,
        default=default_from_date(),
        help="Start date of the synchronization range [YYYY-MM-DD] (optional).",
    )
    parser.add_argument(
        "--to-date",
        type=str,
        default=default_to_date(),
        help="End date of the synchronization range [YYYY-MM-DD] (optional).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="~/downloads/",
        help="Directory where files will be saved (default: system downloads folder)",
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="Path to the YAML configuration file (power zones, lap button duration, etc.)",
    )

    args = parser.parse_args()

    # Call the core application logic
    run_sync_logic(
        args.user,
        args.password,
        args.sport,
        args.from_date,
        args.to_date,
        args.output_dir,
        args.config_file,
    )


if __name__ == "__main__":
    main()
