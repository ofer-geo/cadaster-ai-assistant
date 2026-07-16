select
    p.parcel_version_id,
    p.parcel_uid,
    p.plot_number,
    p.parent_parcel_uid,
    p.status,
    p.valid_from,
    p.valid_to,

    p.valid_to is null as is_current,

    (
        p.valid_to is null
        and p.status = 'approved'
    ) as is_current_approved,

    (
        p.valid_to is null
        and p.status = 'in_process'
    ) as is_current_in_process,

    p.district_id,
    d.district_name,
    p.geom

from {{ ref('stg_parcels') }} p

left join {{ ref('stg_districts') }} d
    on p.district_id = d.district_id

where p.valid_to is null