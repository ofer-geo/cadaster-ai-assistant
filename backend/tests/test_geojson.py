import json

from backend.database.repository import get_parcels_geojson

geojson = get_parcels_geojson([1])  # replace 1 with a real parcel_version_id

print(json.dumps(geojson, indent=2))