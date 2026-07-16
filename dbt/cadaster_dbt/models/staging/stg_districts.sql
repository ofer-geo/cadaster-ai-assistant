select
    district_id,
    district_name,
    geom
from {{ source('raw', 'districts') }}