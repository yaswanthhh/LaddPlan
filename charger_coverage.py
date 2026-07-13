import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

COVERAGE_LIMIT_KM = 30
EXISTING_CHARGERS = ["Malmo"]
NEW_CHARGER_BUDGET = 3

graph = nx.Graph()

roads = [
    ("Malmo", "Lund", 18),
    ("Malmo", "Trelleborg", 32),
    ("Malmo", "Vellinge", 15),
    ("Vellinge", "Trelleborg", 20),
    ("Lund", "Eslov", 20),
    ("Lund", "Lomma", 14),
    ("Lomma", "Malmo", 13),
    ("Lomma", "Landskrona", 27),
    ("Eslov", "Helsingborg", 47),
    ("Landskrona", "Helsingborg", 26),
    ("Landskrona", "Kavlinge", 18),
    ("Kavlinge", "Lund", 22),
]

for start, end, distance in roads:
    graph.add_edge(start, end, distance_km=distance)


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

positions = {
    "Helsingborg": (0, 6),
    "Landskrona": (0.8, 4.7),
    "Kavlinge": (2.2, 3.8),
    "Lomma": (2.0, 2.4),
    "Lund": (3.2, 2.2),
    "Eslov": (3.7, 4.0),
    "Malmo": (1.6, 0.8),
    "Vellinge": (0.7, 0.0),
    "Trelleborg": (2.4, -0.3),
}

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
plt.show()

print("\nMap saved to: output/laddplan_coverage.png")