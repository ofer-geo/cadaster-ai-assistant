from langchain.tools import tool

from backend.database.repository import get_current_parcel_records


@tool
def get_current_parcel(parcel_uid: str) -> list[dict]:
    """Return all current records for a specific cadastral parcel.

    Use this when the user asks about the current approved or in-process
    versions of a parcel.

    Args:
        parcel_uid: Parcel identifier, for example PAR-003.
    """
    return get_current_parcel_records(parcel_uid)