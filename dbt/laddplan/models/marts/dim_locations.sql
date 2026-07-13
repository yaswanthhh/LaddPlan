select
    location_id,
    location_name,
    x_coordinate,
    y_coordinate,
    loaded_at
from {{ ref('stg_locations') }}