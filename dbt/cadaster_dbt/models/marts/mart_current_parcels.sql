select
    parcel_version_id,
    parcel_uid,
    plot_number,
    parent_parcel_uid,
    status,
    valid_from,
    valid_to,

    true as is_current,

    status = 'approved' as is_current_approved,

    status = 'in_process' as is_current_in_process,

    district_id,
    district_name

from {{ ref('mart_parcel_history') }}

where valid_to is null