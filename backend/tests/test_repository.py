from backend.database.repository import get_current_parcel_records

records = get_current_parcel_records("PAR-003")

print(records)