CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS raw.roads (
    road_id SERIAL PRIMARY KEY,
    start_location TEXT NOT NULL,
    end_location TEXT NOT NULL,
    distance_km NUMERIC(10, 2) NOT NULL CHECK (distance_km > 0),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.locations (
    location_id SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL UNIQUE,
    x_coordinate NUMERIC(10, 4) NOT NULL,
    y_coordinate NUMERIC(10, 4) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics.recommendation_runs (
    run_id SERIAL PRIMARY KEY,
    app_name TEXT NOT NULL,
    coverage_limit_km NUMERIC(10, 2) NOT NULL,
    total_locations INTEGER NOT NULL,
    covered_locations INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics.recommended_chargers (
    recommendation_id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES analytics.recommendation_runs(run_id),
    location_name TEXT NOT NULL,
    recommendation_order INTEGER NOT NULL
);