from langchain.tools import tool

from backend.database.repository import (
    get_current_parcel_records,
    get_parcel_history,
    get_parcel_overlaps,
)

@tool
def get_current_parcel(parcel_uid: str) -> list[dict]:
    """Return all current records for a specific cadastral parcel.

    Use this when the user asks about the current approved or in-process
    versions of a parcel.

    Args:
        parcel_uid: Parcel identifier, for example PAR-003.
    """
    return get_current_parcel_records(parcel_uid)


@tool
def get_parcel_history_tool(parcel_uid: str) -> dict:
    """Return the full version history of a cadastral parcel.

    Use this when the user asks about previous versions, geometry changes,
    validity dates, or the historical lifecycle of a parcel.

    Args:
        parcel_uid: Parcel identifier, for example PAR-003.
    """
    return get_parcel_history(parcel_uid)


@tool
def get_parcels_by_area(
    area_name: str,
    status: str | None = None,
) -> list[dict]:
    """Return current parcels within an administrative area.

    Use this when the user asks which parcels are located in a named area,
    or asks for approved or in-process parcels in that area.

    For now, the administrative area is matched against district names.

    Args:
        area_name: Administrative area name, for example Mjini.
        status: Optional parcel status, such as approved or in_process.
    """
    return get_current_parcels_by_area(
        area_name=area_name,
        status=status,
    )


@tool
def get_parcel_overlaps_tool(
    area_name: str | None = None,
    area_type: str | None = None,
    parcel_uid: str | None = None,
) -> list[dict]:
    """Return current parcel overlap conflicts.

    Use this when the user asks:
    - which parcels overlap;
    - whether a specific parcel overlaps another parcel;
    - which overlaps exist in a named administrative area.

    Args:
        area_name: Optional administrative area name, for example Mjini.
        area_type: Administrative level, currently only district.
        parcel_uid: Optional parcel identifier, for example PAR-003.
    """
    return get_parcel_overlaps(
        area_name=area_name,
        area_type=area_type,
        parcel_uid=parcel_uid,
    )