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