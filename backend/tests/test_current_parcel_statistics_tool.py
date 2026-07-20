from backend.tools.parcel_tools import get_parcel_statistics_tool


result = get_parcel_statistics_tool.invoke(
    {
        "status": None,
        "district_name": None,
        "lifecycle": "retired",
    }
)

print(result)