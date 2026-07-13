# LaddPlan

A simple EV charger coverage planner for Skåne, Sweden.

LaddPlan models selected towns as a road network and recommends new EV charger locations that maximize coverage within a chosen driving-distance limit.

![LaddPlan charger coverage map](output/laddplan_coverage.png)

## Current scenario

- Existing charger: Malmö
- Coverage limit: 30 km
- New charger budget: 3
- Recommended locations: Landskrona, Lund, and Trelleborg
- Final coverage: 9 of 9 locations

## How it works

1. Locations are represented as nodes in a graph.
2. Roads are represented as weighted edges, using distance in kilometres.
3. Dijkstra's algorithm calculates the shortest road distance from every location to its nearest charger.
4. A location is covered if its nearest charger is within 30 km.
5. A greedy algorithm tests each possible new charger location and selects the option that increases coverage the most.
6. The process repeats until the charger budget is used.

## Tech stack

- Python
- NetworkX
- Matplotlib

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python charger_coverage.py
```

## Current limitations

- The road distances are manually defined for learning purposes.
- The model uses locations, not real road coordinates.
- It optimizes coverage only; it does not yet consider charger cost, demand, battery range, live availability, or charging speed.

## Next improvements

- Read towns and roads from CSV files
- Add a user-configurable coverage limit and charger budget
- Use real charging-station data
- Use a real road network and travel times
- Add an outage scenario to test backup charger coverage