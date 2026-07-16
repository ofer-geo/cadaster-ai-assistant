from backend.tools.parcel_tools import get_current_parcel


result = get_current_parcel.invoke(
    {"parcel_uid": "PAR-003"}
)

print(result)