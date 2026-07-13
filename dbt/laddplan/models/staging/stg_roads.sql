select
    road_id,
    trim(start_location) as start_location,
    trim(end_location) as end_location,
    distance_km,
    loaded_at
from {{ source('raw', 'roads') }}
where distance_km > 0