from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from .settings import settings

@contextmanager
def db():
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
