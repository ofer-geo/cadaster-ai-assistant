from backend.tools.parcel_tools import get_parcel_overlaps_tool


result = get_parcel_overlaps_tool.invoke(
    {
        "area_name": "Mjini",
        "area_type": "district",
        "parcel_uid": None,
    }
)

print(result)