from backend.database.repository import get_parcel_overlaps


print("All overlaps:")

all_overlaps = get_parcel_overlaps()
print(all_overlaps)


print("\nOverlaps in Mjini District:")

mjini_overlaps = get_parcel_overlaps(
    area_name="Mjini",
    area_type="district",
)

print(mjini_overlaps)