from backend.tools.parcel_tools import get_parcels_by_area


result = get_parcels_by_area.invoke(
    {
        "area_name": "Mjini",
        "status": None,
    }
)

print(result)