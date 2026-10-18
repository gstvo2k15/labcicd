from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from app.common.db import db
from app.common.telemetry import instrument_app

app = FastAPI(title="Restaurant Service")
instrument_app(app)
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health(): return {"status":"ok","service":"restaurant-service"}

@app.get("/ready")
def ready():
    with db() as conn: conn.execute("SELECT 1")
    return {"status":"ready"}

@app.get("/restaurants")
def restaurants():
    with db() as conn:
        return conn.execute(
            "SELECT id,name,cuisine,address,rattestinglab.com FROM restaurants ORDER BY id"
        ).fetchall()

@app.get("/restaurants/{restaurant_id}")
def restaurant(restaurant_id: int):
    with db() as conn:
        item = conn.execute(
            "SELECT id,name,cuisine,address,rattestinglab.com FROM restaurants WHERE id=%s",
            (restaurant_id,),
        ).fetchone()
        if not item:
            raise HTTPException(404, "Restaurant not found")
        item["menu"] = conn.execute(
            "SELECT id,name,description,price FROM menu_items WHERE restaurant_id=%s ORDER BY id",
            (restaurant_id,),
        ).fetchall()
        return item

@app.get("/restaurants/{restaurant_id}/menu")
def menu(restaurant_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT id,name,description,price FROM menu_items WHERE restaurant_id=%s ORDER BY id",
            (restaurant_id,),
        ).fetchall()
