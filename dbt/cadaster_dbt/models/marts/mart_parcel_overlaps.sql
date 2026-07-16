with current_parcels as (

    select
        parcel_version_id,
        parcel_uid,
        plot_number,
        status,
        district_id,
        district_name,
        geom

    from {{ ref('mart_current_parcels') }}

    where valid_to is null
      and status in ('approved', 'in_process')

),

overlap_candidates as (

    select
        a.parcel_version_id as parcel_version_id_1,
        a.parcel_uid as parcel_uid_1,
        a.plot_number as plot_number_1,
        a.status as status_1,

        b.parcel_version_id as parcel_version_id_2,
        b.parcel_uid as parcel_uid_2,
        b.plot_number as plot_number_2,
        b.status as status_2,

        a.district_id as district_id_1,
        a.district_name as district_name_1,

        b.district_id as district_id_2,
        b.district_name as district_name_2,

        ST_Area(a.geom) as parcel_area_m2_1,
        ST_Area(b.geom) as parcel_area_m2_2,

        ST_Intersection(a.geom, b.geom) as overlap_geom

    from current_parcels a

    join current_parcels b
        on a.parcel_version_id < b.parcel_version_id

        -- Do not compare approved and in-process versions
        -- of the same logical parcel.
        and a.parcel_uid <> b.parcel_uid

        -- Fast spatial candidate check.
        and a.geom && b.geom

        -- Exact spatial check.
        and ST_Intersects(a.geom, b.geom)

)

select
    row_number() over (
        order by parcel_version_id_1, parcel_version_id_2
    ) as overlap_id,

    parcel_version_id_1,
    parcel_uid_1,
    plot_number_1,
    status_1,

    parcel_version_id_2,
    parcel_uid_2,
    plot_number_2,
    status_2,

    district_id_1,
    district_name_1,
    district_id_2,
    district_name_2,

    parcel_area_m2_1,
    parcel_area_m2_2,

    ST_Area(overlap_geom) as overlap_area_m2,

    round(
        (
            ST_Area(overlap_geom)
            / nullif(parcel_area_m2_1, 0)
            * 100
        )::numeric,
        2
    ) as overlap_percentage_1,

    round(
        (
            ST_Area(overlap_geom)
            / nullif(parcel_area_m2_2, 0)
            * 100
        )::numeric,
        2
    ) as overlap_percentage_2,

    overlap_geom

from overlap_candidates

where not ST_IsEmpty(overlap_geom)
  and ST_Area(overlap_geom) > 0