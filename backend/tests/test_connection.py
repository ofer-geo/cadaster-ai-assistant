from backend.database.connection import get_connection

print("Starting database test...")

with get_connection() as conn:

    print("Connected to PostgreSQL.")

    with conn.cursor() as cur:

        print("Running query...")

        cur.execute("""
            SELECT COUNT(*)
            FROM analytics.mart_current_parcels
        """)

        result = cur.fetchone()

        print("Result:", result)

print("Connection closed.")