import time
from backend.tools.parcel_tools import get_parcel_history_tool

start = time.perf_counter()

result = get_parcel_history_tool.invoke(
    {"parcel_uid": "PAR-100"}
)

elapsed = time.perf_counter() - start

print(result)
print(f"\nTool time: {elapsed:.3f} seconds")