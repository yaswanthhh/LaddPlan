import csv
import json
from pathlib import Path

OUTPUT_DIR = Path("output")
SUMMARY_FILE = OUTPUT_DIR / "scenario_summary.csv"

rows = []

for file_path in sorted(OUTPUT_DIR.glob("*_recommendations.json")):
    scenario_name = file_path.name.replace("_recommendations.json", "")

    with file_path.open(encoding="utf-8") as file:
        result = json.load(file)

    rows.append(
        {
            "scenario": scenario_name,
            "coverage_limit_km": result["coverage_limit_km"],
            "existing_chargers": ", ".join(result["existing_chargers"]),
            "recommended_chargers": ", ".join(
                result["recommended_chargers"]
            ),
            "total_locations": result["total_locations"],
            "covered_locations": result["covered_locations"],
            "uncovered_locations": ", ".join(
                result["uncovered_locations"]
            )
            or "None",
            "coverage_percent": round(
                result["covered_locations"]
                / result["total_locations"]
                * 100,
                1,
            ),
        }
    )

with SUMMARY_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Scenario summary saved to: {SUMMARY_FILE}")