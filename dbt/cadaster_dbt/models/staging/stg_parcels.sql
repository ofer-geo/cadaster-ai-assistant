select
    parcel_version_id,
    parcel_uid,
    plot_number,
    district_id,
    parent_parcel_uid,
    status,
    valid_from,
    valid_to,
    geom
from {{ source('raw', 'parcels') }}