select distinct
    child.parent_parcel_uid,
    child.parcel_uid as child_parcel_uid,

    child.valid_from as relationship_date,

    parent.parcel_version_id as parent_version_id,
    parent.valid_from as parent_valid_from,
    parent.valid_to as parent_valid_to,

    child.parcel_version_id as child_version_id,
    child.status as child_status,
    child.valid_from as child_valid_from,
    child.valid_to as child_valid_to,

    child.district_id,
    child.district_name

from {{ ref('mart_parcel_history') }} child

left join {{ ref('mart_parcel_history') }} parent
    on child.parent_parcel_uid = parent.parcel_uid

where child.parent_parcel_uid is not null