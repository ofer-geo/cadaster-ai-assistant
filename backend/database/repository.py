from psycopg.rows import dict_row

from backend.database.connection import get_connection


def get_current_parcel_records(parcel_uid: str) -> list[dict]:
    """Return all current records for one parcel UID."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    parcel_version_id,
                    parcel_uid,
                    plot_number,
                    parent_parcel_uid,
                    status,
                    valid_from,
                    valid_to,
                    is_current,
                    is_current_approved,
                    is_current_in_process,
                    district_id,
                    district_name
                FROM analytics.mart_current_parcels
                WHERE parcel_uid = %s
                ORDER BY
                    CASE
                        WHEN status = 'approved' THEN 1
                        WHEN status = 'in_process' THEN 2
                        ELSE 3
                    END,
                    valid_from
                """,
                (parcel_uid,),
            )

            return cur.fetchall()



def get_parcel_history(parcel_uid: str) -> dict:
    """Return parcel versions and parent-child lineage."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    parcel_version_id,
                    parcel_uid,
                    plot_number,
                    parent_parcel_uid,
                    status,
                    valid_from,
                    valid_to,
                    temporal_state,
                    version_number,
                    district_id,
                    district_name
                FROM analytics.mart_parcel_history
                WHERE parcel_uid = %s
                ORDER BY version_number
                """,
                (parcel_uid,),
            )

            versions = cur.fetchall()

    lineage = get_parcel_lineage(parcel_uid)

    return {
        "parcel_uid": parcel_uid,
        "versions": versions,
        "lineage": lineage,
    }


def get_current_parcels_by_area(
    area_name: str,
    status: str | None = None,
) -> list[dict]:
    """Return current parcel records in an administrative area.

    For now, area_name is matched against district_name.
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    parcel_version_id,
                    parcel_uid,
                    plot_number,
                    parent_parcel_uid,
                    status,
                    valid_from,
                    district_id,
                    district_name
                FROM analytics.mart_current_parcels
                WHERE lower(district_name) = lower(%s)
                  AND (%s IS NULL OR status = %s)
                ORDER BY parcel_uid, status
                """,
                (area_name, status, status),
            )

            return cur.fetchall()


def get_parcel_lineage(parcel_uid: str) -> dict:
    """Return parent and child relationships for one parcel."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    parent_parcel_uid,
                    child_parcel_uid,
                    relationship_date,
                    parent_version_id,
                    parent_valid_from,
                    parent_valid_to,
                    child_version_id,
                    child_status,
                    child_valid_from,
                    child_valid_to,
                    district_id,
                    district_name
                FROM analytics.mart_parcel_lineage
                WHERE parent_parcel_uid = %s
                   OR child_parcel_uid = %s
                ORDER BY relationship_date, child_parcel_uid
                """,
                (parcel_uid, parcel_uid),
            )

            rows = cur.fetchall()

    parent = None
    children = []

    for row in rows:
        if row["child_parcel_uid"] == parcel_uid:
            parent = {
                "parcel_uid": row["parent_parcel_uid"],
                "relationship_date": row["relationship_date"],
                "valid_from": row["parent_valid_from"],
                "valid_to": row["parent_valid_to"],
            }

        if row["parent_parcel_uid"] == parcel_uid:
            children.append(
                {
                    "parcel_uid": row["child_parcel_uid"],
                    "relationship_date": row["relationship_date"],
                    "status": row["child_status"],
                    "valid_from": row["child_valid_from"],
                    "valid_to": row["child_valid_to"],
                }
            )

    return {
        "parent": parent,
        "children": children,
    }



def get_parcel_overlaps(
    area_name: str | None = None,
    area_type: str | None = None,
    parcel_uid: str | None = None,
) -> list[dict]:
    """Return current parcel overlap conflicts with optional filters."""

    area_columns = {
        "district": ("district_name_1", "district_name_2"),
        # Later:
        # "region": ("region_name_1", "region_name_2"),
        # "ward": ("ward_name_1", "ward_name_2"),
    }

    conditions: list[str] = []
    parameters: list[object] = []

    if parcel_uid is not None:
        conditions.append(
            "(parcel_uid_1 = %s OR parcel_uid_2 = %s)"
        )
        parameters.extend([parcel_uid, parcel_uid])

    if area_name is not None:
        if area_type is None:
            raise ValueError(
                "area_type must be provided when area_name is used."
            )

        normalized_area_type = area_type.lower()

        if normalized_area_type not in area_columns:
            supported = ", ".join(area_columns)

            raise ValueError(
                f"Unsupported area type: {area_type}. "
                f"Supported area types: {supported}"
            )

        area_column_1, area_column_2 = area_columns[
            normalized_area_type
        ]

        conditions.append(
            f"""
            (
                lower({area_column_1}) = lower(%s)
                OR lower({area_column_2}) = lower(%s)
            )
            """
        )

        parameters.extend([area_name, area_name])

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT
            overlap_id,

            parcel_uid_1,
            plot_number_1,
            status_1,

            parcel_uid_2,
            plot_number_2,
            status_2,

            district_name_1,
            district_name_2,

            overlap_area_m2,
            overlap_percentage_1,
            overlap_percentage_2

        FROM analytics.mart_parcel_overlaps

        {where_clause}

        ORDER BY overlap_area_m2 DESC
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, tuple(parameters))
            return cur.fetchall()