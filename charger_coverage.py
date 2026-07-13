import networkx as nx

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

print("LaddRäckvidd - EV Charger Coverage Simulator")
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
        print(f"\nRound {round_number}: No location can improve coverage.")
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

remaining_uncovered = set(graph.nodes) - current_coverage
print(f"Final coverage: {len(current_coverage)} / {graph.number_of_nodes()} locations")

if remaining_uncovered:
    print(f"Still uncovered: {', '.join(sorted(remaining_uncovered))}")
else:
    print("All locations are covered!")