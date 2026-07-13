select
    location_id,
    trim(location_name) as location_name,
    x_coordinate,
    y_coordinate,
    loaded_at
from {{ source('raw', 'locations') }}
where location_name is not null