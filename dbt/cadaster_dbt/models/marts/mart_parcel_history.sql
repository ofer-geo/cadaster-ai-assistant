select
    p.parcel_version_id,
    p.parcel_uid,
    p.plot_number,
    p.parent_parcel_uid,
    p.status,
    p.valid_from,
    p.valid_to,

    case
        when p.valid_to is null then 'current'
        else 'historical'
    end as temporal_state,

    row_number() over (
        partition by p.parcel_uid
        order by p.valid_from, p.parcel_version_id
    ) as version_number,

    p.district_id,
    d.district_name,

    p.geom

from {{ ref('stg_parcels') }} p

left join {{ ref('stg_districts') }} d
    on p.district_id = d.district_id