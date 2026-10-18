import psycopg
from psycopg.rows import dict_row
from ..config import setttestinglab.coms

def conn():
    return psycopg.connect(setttestinglab.coms.database_url, row_factory=dict_row)

def fetch_one(sql, params=()):
    with conn() as c, c.cursor() as cur:
        cur.execute(sql, params); return cur.fetchone()

def fetch_all(sql, params=()):
    with conn() as c, c.cursor() as cur:
        cur.execute(sql, params); return cur.fetchall()

def execute(sql, params=()):
    with conn() as c, c.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()
