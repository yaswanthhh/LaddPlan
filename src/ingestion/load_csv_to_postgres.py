import csv
from pathlib import Path

import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "laddplan",
    "user": "laddplan_user",
    "password": "laddplan_password",
}


def load_locations(connection):
    locations_file = PROJECT_ROOT / "data" / "locations.csv"

    with locations_file.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE raw.locations RESTART IDENTITY CASCADE")

        for row in rows:
            cursor.execute(
                """
                INSERT INTO raw.locations (
                    location_name,
                    x_coordinate,
                    y_coordinate
                )
                VALUES (%s, %s, %s)
                """,
                (
                    row["location"],
                    float(row["x"]),
                    float(row["y"]),
                ),
            )

    print(f"Loaded {len(rows)} locations into raw.locations")


def load_roads(connection):
    roads_file = PROJECT_ROOT / "data" / "roads.csv"

    with roads_file.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE raw.roads RESTART IDENTITY")

        for row in rows:
            cursor.execute(
                """
                INSERT INTO raw.roads (
                    start_location,
                    end_location,
                    distance_km
                )
                VALUES (%s, %s, %s)
                """,
                (
                    row["start"],
                    row["end"],
                    float(row["distance_km"]),
                ),
            )

    print(f"Loaded {len(rows)} roads into raw.roads")


def main():
    with psycopg.connect(**DATABASE_CONFIG) as connection:
        load_locations(connection)
        load_roads(connection)
        connection.commit()

    print("CSV ingestion completed successfully.")


if __name__ == "__main__":
    main()