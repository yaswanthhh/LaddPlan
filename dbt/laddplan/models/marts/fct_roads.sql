select
    road_id,
    start_location,
    end_location,
    distance_km,
    loaded_at
from {{ ref('stg_roads') }}