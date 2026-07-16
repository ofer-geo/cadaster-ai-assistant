from fastapi import FastAPI, HTTPException

from backend.database.repository import get_current_parcel_records


app = FastAPI(
    title="Cadaster AI Assistant API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple indication that the backend is running."""
    return {"status": "ok"}

@app.get("/parcels/{parcel_uid}")
def get_parcel(parcel_uid: str) -> dict:
    records = get_current_parcel_records(parcel_uid)

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"Parcel {parcel_uid} was not found.",
        )

    return {
        "parcel_uid": parcel_uid,
        "records": records,
    }