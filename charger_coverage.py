import csv
import json
import psycopg
import matplotlib
import os

import networkx as nx
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATABASE_CONFIG = {
    "host": os.getenv("LADDPLAN_DB_HOST", "localhost"),
    "port": int(os.getenv("LADDPLAN_DB_PORT", "5433")),
    "dbname": os.getenv("LADDPLAN_DB_NAME", "laddplan"),
    "user": os.getenv("LADDPLAN_DB_USER", "laddplan_user"),
    "password": os.getenv("LADDPLAN_DB_PASSWORD", "laddplan_password"),
}

def load_config():
    with open("config.json", encoding="utf-8") as file:
        return json.load(file)

def load_network_from_database():
    graph = nx.Graph()
    positions = {}

    with psycopg.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    start_location,
                    end_location,
                    distance_km
                FROM analytics.fct_roads
                ORDER BY road_id
                """
            )

            for start, end, distance in cursor.fetchall():
                graph.add_edge(
                    start,
                    end,
                    distance_km=float(distance),
                )

            cursor.execute(
                """
                SELECT
                    location_name,
                    x_coordinate,
                    y_coordinate
                FROM analytics.dim_locations
                ORDER BY location_name
                """
            )

            for location, x_coordinate, y_coordinate in cursor.fetchall():
                positions[location] = (
                    float(x_coordinate),
                    float(y_coordinate),
                )

    return graph, positions

graph, positions = load_network_from_database()


def get_covered_locations(chargers):
    distances = nx.multi_source_dijkstra_path_length(
        graph,
        sources=chargers,
        weight="distance_km",
    )

    return {
        location
        for location, distance in distances.items()
        if distance <= COVERAGE_LIMIT_KM
    }

def load_positions():
    positions = {}

    with open("data/locations.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            positions[row["location"]] = (
                float(row["x"]),
                float(row["y"]),
            )

    return positions

def save_recommendations(
    existing_chargers,
    recommended_chargers,
    coverage_limit_km,
    total_locations,
    covered_locations,
):
    result = {
        "app_name": "LaddPlan",
        "coverage_limit_km": coverage_limit_km,
        "existing_chargers": existing_chargers,
        "recommended_chargers": recommended_chargers,
        "total_locations": total_locations,
        "covered_locations": len(covered_locations),
        "uncovered_locations": sorted(
            set(graph.nodes) - covered_locations
        ),
    }

    with open(
        "output/recommendations.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(result, file, indent=2)

    return result

config = load_config()

COVERAGE_LIMIT_KM = config["coverage_limit_km"]
EXISTING_CHARGERS = config["existing_chargers"]
NEW_CHARGER_BUDGET = config["new_charger_budget"]

selected_chargers = EXISTING_CHARGERS.copy()
current_coverage = get_covered_locations(selected_chargers)

print("LaddPlan - EV Charger Coverage Simulator")
print(f"\nExisting chargers: {', '.join(EXISTING_CHARGERS)}")
print(f"Coverage limit: {COVERAGE_LIMIT_KM} km")
print(f"New charger budget: {NEW_CHARGER_BUDGET}")
print(f"\nStarting coverage: {len(current_coverage)} / {graph.number_of_nodes()} locations")

for round_number in range(1, NEW_CHARGER_BUDGET + 1):
    best_location = None
    best_coverage = current_coverage

    for candidate in graph.nodes:
        if candidate in selected_chargers:
            continue

        trial_chargers = selected_chargers + [candidate]
        trial_coverage = get_covered_locations(trial_chargers)

        if len(trial_coverage) > len(best_coverage):
            best_location = candidate
            best_coverage = trial_coverage

    if best_location is None:
        break

    newly_covered = best_coverage - current_coverage
    selected_chargers.append(best_location)
    current_coverage = best_coverage

    print(f"\nRound {round_number}")
    print(f"Recommended location: {best_location}")
    print(f"Newly covered: {', '.join(sorted(newly_covered))}")
    print(f"Coverage now: {len(current_coverage)} / {graph.number_of_nodes()} locations")

print("\nFinal charger plan:")
print(", ".join(selected_chargers))
print(f"Final coverage: {len(current_coverage)} / {graph.number_of_nodes()} locations")

new_chargers = [
    location for location in selected_chargers
    if location not in EXISTING_CHARGERS
]

node_colors = []
for location in graph.nodes:
    if location in EXISTING_CHARGERS:
        node_colors.append("#1f77b4")
    elif location in new_chargers:
        node_colors.append("#2ca02c")
    elif location in current_coverage:
        node_colors.append("#a7d8f0")
    else:
        node_colors.append("#e74c3c")

plt.figure(figsize=(11, 8))

nx.draw_networkx_edges(
    graph,
    positions,
    edge_color="#7f8c8d",
    width=1.8,
)

nx.draw_networkx_nodes(
    graph,
    positions,
    node_color=node_colors,
    node_size=1300,
    edgecolors="#2c3e50",
    linewidths=1.2,
)

nx.draw_networkx_labels(
    graph,
    positions,
    font_size=9,
    font_weight="bold",
)

edge_labels = nx.get_edge_attributes(graph, "distance_km")
edge_labels = {edge: f"{distance} km" for edge, distance in edge_labels.items()}

nx.draw_networkx_edge_labels(
    graph,
    positions,
    edge_labels=edge_labels,
    font_size=8,
)

legend_items = [
    Patch(facecolor="#1f77b4", edgecolor="#2c3e50", label="Existing charger"),
    Patch(facecolor="#2ca02c", edgecolor="#2c3e50", label="Recommended charger"),
    Patch(facecolor="#a7d8f0", edgecolor="#2c3e50", label="Covered location"),
    Patch(facecolor="#e74c3c", edgecolor="#2c3e50", label="Uncovered location"),
]

plt.legend(handles=legend_items, loc="upper right")
plt.title(
    "LaddPlan: EV Charger Coverage Plan\n"
    f"Coverage: {len(current_coverage)} / {graph.number_of_nodes()} locations",
    fontsize=15,
    fontweight="bold",
)
plt.axis("off")
plt.tight_layout()
plt.savefig("output/laddplan_coverage.png", dpi=200, bbox_inches="tight")

print("\nMap saved to: output/laddplan_coverage.png")
recommended_chargers = [
    location
    for location in selected_chargers
    if location not in EXISTING_CHARGERS
]

save_recommendations(
    existing_chargers=EXISTING_CHARGERS,
    recommended_chargers=recommended_chargers,
    coverage_limit_km=COVERAGE_LIMIT_KM,
    total_locations=graph.number_of_nodes(),
    covered_locations=current_coverage,
)

def save_run_to_database(
    existing_chargers,
    recommended_chargers,
    coverage_limit_km,
    total_locations,
    covered_locations,
):
    with psycopg.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analytics.recommendation_runs (
                    app_name,
                    coverage_limit_km,
                    total_locations,
                    covered_locations
                )
                VALUES (%s, %s, %s, %s)
                RETURNING run_id
                """,
                (
                    "LaddPlan",
                    coverage_limit_km,
                    total_locations,
                    len(covered_locations),
                ),
            )

            run_id = cursor.fetchone()[0]

            for order, location in enumerate(
                recommended_chargers,
                start=1,
            ):
                cursor.execute(
                    """
                    INSERT INTO analytics.recommended_chargers (
                        run_id,
                        location_name,
                        recommendation_order
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (run_id, location, order),
                )

    return run_id

run_id = save_run_to_database(
    existing_chargers=EXISTING_CHARGERS,
    recommended_chargers=recommended_chargers,
    coverage_limit_km=COVERAGE_LIMIT_KM,
    total_locations=graph.number_of_nodes(),
    covered_locations=current_coverage,
)

print(f"Recommendation run saved to Postgres with run_id: {run_id}")
print("Recommendations saved to: output/recommendations.json")