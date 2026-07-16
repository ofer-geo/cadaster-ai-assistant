import psycopg


def get_connection():
    """Create and return a new PostgreSQL connection."""

    return psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname="cadaster",
        user="cadaster",
        password="cadaster",
    )