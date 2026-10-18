from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from .setttestinglab.coms import setttestinglab.coms

@contextmanager
def db():
    conn = psycopg.connect(setttestinglab.coms.database_url, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
