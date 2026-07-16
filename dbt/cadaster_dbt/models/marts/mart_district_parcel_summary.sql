select
    d.district_id,
    d.district_name,

    count(p.parcel_version_id) filter (
        where p.valid_to is null
    ) as current_parcel_count,

    count(p.parcel_version_id) filter (
        where p.valid_to is null
          and p.status = 'approved'
    ) as approved_current_parcel_count,

    count(p.parcel_version_id) filter (
        where p.valid_to is null
          and p.status = 'in_process'
    ) as in_process_current_parcel_count,

    count(p.parcel_version_id) filter (
        where p.valid_to is not null
    ) as historical_version_count,

    d.geom

from {{ ref('stg_districts') }} d

left join {{ ref('stg_parcels') }} p
    on d.district_id = p.district_id

group by
    d.district_id,
    d.district_name,
    d.geom